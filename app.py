import streamlit as st  # ✅ Streamlit must be imported first!
import requests
import asyncio
import json
import os
from main import run_long
from src.utils.split_text import clean_text
from PyPDF2 import PdfReader
from io import BytesIO
from fpdf import FPDF
from langdetect import detect
from googletrans import Translator

# ✅ Initialize Translator
translator = Translator()

# ✅ Set page title and layout
st.set_page_config(page_title="Autodictionary", layout="wide")

# 🎨 Custom CSS for better UI
st.markdown(
    """
    <style>
    h1, h2, h3, h4, h5, h6, .stText, .stMarkdown, label {
        color: #004aad !important; /* Deep blue color */
    }
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

# ✅ Function to extract text from uploaded PDF or TXT files
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

# ✅ Function to download & extract text from a PDF URL
def extract_text_from_pdf_url(pdf_url):
    try:
        # Download the PDF file
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        # Save the PDF temporarily
        temp_pdf_path = "temp_research_paper.pdf"
        with open(temp_pdf_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)

        # Extract text from the PDF
        pdf_reader = PdfReader(temp_pdf_path)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        # Delete temporary file
        os.remove(temp_pdf_path)

        return text if text else "No readable text found in the PDF."
    
    except requests.exceptions.RequestException as e:
        return f"Error downloading PDF: {e}"
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

# ✅ Detect the language of the text
def detect_language(text):
    try:
        return detect(text)
    except:
        return "Unknown"

# ✅ Translate text to English
def translate_text(text, target_lang="en"):
    try:
        return translator.translate(text, dest=target_lang).text
    except:
        return "Translation failed."

# ✅ Convert JSON to a text file
def download_as_text(data):
    return BytesIO(json.dumps(data, indent=4).encode("utf-8"))

# ✅ Convert JSON to a PDF file
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

# 🏆 **Page Header**
st.title("📖 Autodictionary - Intelligent Word Extraction")

# 📂 **File Upload Section**
st.sidebar.header("Upload Your Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or TXT files", 
    type=["pdf", "txt"], 
    accept_multiple_files=True
)

# 🌐 **PDF URL Input Section**
st.sidebar.subheader("Extract from PDF URL")
pdf_url_input = st.sidebar.text_input("Enter the URL of a research paper PDF:")

# 📌 **Text Extraction Logic**
text = ""

# 📂 Process Uploaded Files
if uploaded_files:
    text = extract_text_from_file(uploaded_files)

# 🌐 Process PDF URL Input
elif pdf_url_input:
    st.sidebar.write("🔄 Downloading & Extracting text from PDF...")
    text = extract_text_from_pdf_url(pdf_url_input)

# 📜 **Display Extracted Text**
if text:
    with st.expander("📜 Extracted Text Preview", expanded=False):
        st.text_area("Extracted Text", text[:2000], height=300)

    # 🌍 **Language Detection & Translation**
    detected_lang = detect_language(text)
    st.sidebar.write(f"**Detected Language:** `{detected_lang.upper()}`")

    if detected_lang != "en":
        if st.sidebar.button("🌍 Translate to English"):
            translated_text = translate_text(text, "en")
            with st.expander("📖 Translated Text", expanded=True):
                st.text_area("Translated Text", translated_text[:2000], height=300)
            text = translated_text  # Update for processing

    # ⚡ **Process Extracted Text**
    if st.button("⚡ Process Extracted Text"):
        with st.spinner("Processing... Please wait."):
            try:
                output = asyncio.run(run_long(clean_text(text)))
                if isinstance(output, dict):
                    with st.expander("📌 Extracted Words", expanded=True):
                        st.json(output)

                    # 🔍 **Search & Filter**
                    search_query = st.text_input("🔎 Search for a word:")
                    if search_query:
                        filtered_output = {
                            key: val for key, val in output.items() 
                            if search_query.lower() in key.lower()
                        }
                        st.json(filtered_output)

                    # 📥 **Download Options**
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
            except Exception as e:
                st.error(f"An error occurred: {e}")

else:
    st.warning("Please upload a file or enter a PDF URL to extract text.")
