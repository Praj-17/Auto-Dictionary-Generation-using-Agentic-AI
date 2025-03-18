import streamlit as st  # ✅ Streamlit must be imported first!

# Set page title and layout FIRST!
st.set_page_config(page_title="Autodictionary", layout="wide")

import asyncio
import json
from main import run_long
from src.utils.split_text import clean_text
from PyPDF2 import PdfReader
from io import BytesIO
from fpdf import FPDF
from langdetect import detect
from googletrans import Translator

translator = Translator()

# Function to extract text from multiple files
def extract_text_from_file(uploaded_files):
    extracted_texts = []
    
    for uploaded_file in uploaded_files:
        if uploaded_file.type == "text/plain":
            extracted_texts.append(uploaded_file.read().decode("utf-8"))
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            extracted_texts.append(text)

    return "\n\n".join(extracted_texts)  # Combine all extracted texts

# Detect the language of the text
def detect_language(text):
    try:
        return detect(text)
    except:
        return "Unknown"

# Translate text to English
def translate_text(text, target_lang="en"):
    try:
        return translator.translate(text, dest=target_lang).text
    except:
        return "Translation failed."

# Convert JSON to a text file for download
def download_as_text(data):
    return BytesIO(json.dumps(data, indent=4).encode("utf-8"))

# Convert JSON to a PDF file for download
def download_as_pdf(data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in json.dumps(data, indent=4).split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)

    pdf_buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)
    return pdf_buffer

# 🎨 Custom CSS for better UI
st.markdown(
    """
    <style>
    /* Change all headings and text to blue */
    h1, h2, h3, h4, h5, h6, .stText, .stMarkdown, label {
        color: #004aad !important; /* A deep blue color */
    }

    /* Maintain button styling */
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# 🏆 Page Header
st.title("📖 Autodictionary - Intelligent Word Extraction")

# Sidebar Upload Section
st.sidebar.header("Upload Your Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or TXT files", 
    type=["pdf", "txt"], 
    accept_multiple_files=True
)

if uploaded_files:
    text = extract_text_from_file(uploaded_files)
    
    if text:
        # 📝 Display Extracted Text
        with st.expander("📜 Extracted Text Preview", expanded=False):
            st.text_area("Extracted Text", text[:1000], height=200)

        #  Language Detection
        detected_lang = detect_language(text)
        st.sidebar.write(f"**Detected Language:** `{detected_lang.upper()}`")

        #  Translation Option
        if detected_lang != "en":
            if st.sidebar.button("🌍 Translate to English"):
                translated_text = translate_text(text, "en")
                with st.expander("📖 Translated Text", expanded=True):
                    st.text_area("Translated Text", translated_text[:1000], height=200)
                text = translated_text  # Update text for further processing

        #  Process Text Button
        if st.button("⚡ Process Text"):
            with st.spinner("Processing... Please wait."):
                try:
                    output = asyncio.run(run_long(clean_text(text)))
                    
                    if isinstance(output, dict):  # Ensure valid JSON
                        with st.expander("📌 Extracted Words", expanded=True):
                            st.json(output)

                        #  Search & Filter
                        search_query = st.text_input("🔎 Search for a word:")
                        if search_query:
                            filtered_output = {
                                key: val for key, val in output.items() 
                                if search_query.lower() in key.lower()
                            }
                            st.json(filtered_output)

                        # 📥 Download Options
                        with st.expander("📥 Download Processed Output", expanded=False):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    "📄 Download as TXT", 
                                    data=download_as_text(output), 
                                    file_name="extracted_words.txt", 
                                    mime="text/plain"
                                )
                            with col2:
                                st.download_button(
                                    "📂 Download as PDF", 
                                    data=download_as_pdf(output), 
                                    file_name="extracted_words.pdf", 
                                    mime="application/pdf"
                                )

                    else:
                        st.error("Error: Processed output is not valid JSON.")
                        st.write("Raw Output:", output)

                except Exception as e:
                    st.error(f"An error occurred while processing: {e}")

    else:
        st.error("Failed to extract text from the uploaded files.")
