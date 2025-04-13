import streamlit as st  # ✅ Streamlit must be imported first!
from streamlit_pdf_viewer import pdf_viewer  # Integrated PDF viewer
import requests
import asyncio
import json
import os
import torch
import warnings
import base64
import time
import numpy as np
from io import BytesIO
import soundfile as sf
from pypdf import PdfReader
from fpdf import FPDF

# Import helper functions from helpers.py
from src.helpers import (
    extract_text_from_file,
    extract_text_from_pdf_url,
    detect_language,
    translate_text,
    download_as_text,
    download_as_pdf  # Now uses the Kokoro-based TTS
)

# Additional imports used in your app
from src.utils.split_text import clean_text
from main import run_long, run_short  # If defined elsewhere in your codebase
from src.database import get_all_words, search_word  # Import MongoDB functions

# Environment and warning configurations
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"
torch.classes.__path__ = []
warnings.filterwarnings("ignore", message="<built-in function callable> is not a Python type")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.nn.utils.weight_norm")

from src.kokoro_tts import KokoroTTSGenerator  # Adjust the import path if needed
tts = KokoroTTSGenerator(lang_code='es', voice='af_heart')
# ✅ Set page title and layout
st.set_page_config(page_title="Autodictionary", layout="wide")

# ✅ Initialize session state variables
if "processed_output" not in st.session_state:
    st.session_state["processed_output"] = None
if "aggregated_audio" not in st.session_state:
    st.session_state["aggregated_audio"] = None

# 🎨 Custom CSS for UI styling
st.markdown(
    """
    <style>
    h1, h2, h3, h4, h5, h6, .stText, .stMarkdown, label {
        color: #004aad !important;
    }
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 20px;
    }
    .sidebar-section {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================
# Revised TTS Streaming Function
# ============================
def stream_text_to_speech(text):
    """
    Uses the KokoroTTSGenerator to yield concatenated audio chunks.
    For each generated WAV file, the function reads the audio data and appends it
    to st.session_state["aggregated_audio"]. The updated audio is written into a
    BytesIO buffer (with a fresh WAV header) and yielded.
    """

    generator = tts.generate_audio(text)
    sample_rate = 24000  # Use the same sample rate as your TTS generator
    
    # Loop over each generated chunk
    for wav_filename in generator:
        try:
            # Read new chunk from file as numpy array
            data, sr = sf.read(wav_filename)
            # Initialize or concatenate based on session state
            if st.session_state["aggregated_audio"] is None:
                st.session_state["aggregated_audio"] = data
            else:
                st.session_state["aggregated_audio"] = np.concatenate(
                    [st.session_state["aggregated_audio"], data], axis=0
                )
            # Write the updated audio into a new BytesIO buffer with a fresh WAV header
            buffer = BytesIO()
            sf.write(buffer, st.session_state["aggregated_audio"], sample_rate, format='WAV')
            buffer.seek(0)
            yield buffer.read()
        except Exception as e:
            st.error(f"Error processing TTS chunk: {e}")
            break

# ============================
# Sidebar: File Upload & PDF URL Input
# ============================
st.sidebar.header("Upload & PDF URL")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or TXT files", 
    type=["pdf", "txt"], 
    accept_multiple_files=True
)
st.sidebar.subheader("Extract from PDF URL")
pdf_url_input = st.sidebar.text_input("Enter the URL of a research paper PDF:")

# Create an audio placeholder (to be updated during streaming)
audio_placeholder = st.empty()

# ============================
# Main File Viewer & Read Aloud Feature
# ============================
if uploaded_files:
    st.header("📂 File Viewer")
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type
        file_name = uploaded_file.name
        st.subheader(f"File: {file_name}")
        
        if file_type == "application/pdf":
            # --- Read Aloud Button for PDF files ---
            if st.button("🔊 Read Aloud", key=f"{file_name}_read_aloud_top"):
                try:
                    # Reset the aggregated audio before processing
                    st.session_state["aggregated_audio"] = None
                    
                    uploaded_file.seek(0)
                    pdf_reader = PdfReader(uploaded_file)
                    text_content = ""
                    for page in pdf_reader.pages:
                        page_text = page.extract_text() or ""
                        text_content += page_text + "\n"
                    
                    if not text_content.strip():
                        st.warning("No extractable text found for speech.")
                    else:
                        # Stream the TTS audio chunks
                        for chunk in stream_text_to_speech(text_content):
                            b64_audio = base64.b64encode(chunk).decode("utf-8")
                            # Update the HTML audio player and preserve playback position
                            audio_html = f"""
                            <audio id="audio_player" controls autoplay style="width: 100%;">
                                <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
                            </audio>
                            <script>
                            (function() {{
                                var audioElem = document.getElementById('audio_player');
                                var currentTime = audioElem.currentTime || 0;
                                var isPlaying = !audioElem.paused;
                                audioElem.pause();
                                audioElem.src = "data:audio/wav;base64,{b64_audio}";
                                audioElem.load();
                                audioElem.onloadedmetadata = function() {{
                                    audioElem.currentTime = currentTime;
                                    if (isPlaying) {{
                                        audioElem.play();
                                    }}
                                }};
                            }})();
                            </script>
                            """
                            audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
                            time.sleep(1)  # Simulate delay between chunks
                except Exception as e:
                    st.error(f"Text-to-speech error: {e}")
            
            # Display the PDF content below the Read Aloud button.
            with st.expander("View PDF", expanded=True):
                uploaded_file.seek(0)
                pdf_viewer(uploaded_file.getvalue(), width=1000, height=1000)
        
        elif file_type == "text/plain":
            text_content = uploaded_file.read().decode("utf-8")
            uploaded_file.seek(0)
            with st.expander("View File Content", expanded=True):
                st.text_area("Content", text_content, height=600)
            if st.button("🔊 Read Aloud", key=f"{file_name}_read_aloud_text"):
                if not text_content.strip():
                    st.warning("File content is empty.")
                else:
                    try:
                        # Reset the aggregated audio
                        st.session_state["aggregated_audio"] = None
                        
                        for chunk in stream_text_to_speech(text_content):
                            b64_audio = base64.b64encode(chunk).decode("utf-8")
                            audio_html = f"""
                            <audio id="audio_player" controls autoplay style="width: 100%;">
                                <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
                            </audio>
                            <script>
                            (function() {{
                                var audioElem = document.getElementById('audio_player');
                                var currentTime = audioElem.currentTime || 0;
                                var isPlaying = !audioElem.paused;
                                audioElem.pause();
                                audioElem.src = "data:audio/wav;base64,{b64_audio}";
                                audioElem.load();
                                audioElem.onloadedmetadata = function() {{
                                    audioElem.currentTime = currentTime;
                                    if (isPlaying) {{
                                        audioElem.play();
                                    }}
                                }};
                            }})();
                            </script>
                            """
                            audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
                            time.sleep(1)
                    except Exception as e:
                        st.error(f"Text-to-speech error: {e}")

elif pdf_url_input:
    st.info("🔄 Downloading & Extracting text from PDF URL...")
    text_from_url = extract_text_from_pdf_url(pdf_url_input)
    st.header("📄 PDF Content from URL")
    # --- Read Aloud Button for URL PDF ---
    if st.button("🔊 Read Aloud (URL)", key="url_read_aloud_top"):
        if not text_from_url.strip():
            st.warning("No extractable text found from PDF URL.")
        else:
            try:
                st.session_state["aggregated_audio"] = None  # Reset before streaming
                for chunk in stream_text_to_speech(text_from_url):
                    b64_audio = base64.b64encode(chunk).decode("utf-8")
                    audio_html = f"""
                    <audio id="audio_player" controls autoplay style="width: 100%;">
                        <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
                    </audio>
                    <script>
                    (function() {{
                        var audioElem = document.getElementById('audio_player');
                        var currentTime = audioElem.currentTime || 0;
                        var isPlaying = !audioElem.paused;
                        audioElem.pause();
                        audioElem.src = "data:audio/wav;base64,{b64_audio}";
                        audioElem.load();
                        audioElem.onloadedmetadata = function() {{
                            audioElem.currentTime = currentTime;
                            if (isPlaying) {{
                                audioElem.play();
                            }}
                        }};
                    }})();
                    </script>
                    """
                    audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
                    time.sleep(1)
            except Exception as e:
                st.error(f"Text-to-speech error: {e}")
    with st.expander("View PDF Extracted Text", expanded=True):
        st.text_area("Extracted Text", text_from_url, height=600)
else:
    st.info("Please upload a file or enter a PDF URL to extract and view content.")

# ============================
# Sidebar: Process Extracted Text & Database Tools
# ============================
with st.sidebar.container():
    if uploaded_files or pdf_url_input:
        extracted_text = extract_text_from_file(uploaded_files) if uploaded_files else text_from_url
        with st.sidebar.expander("📜 Extracted Text Preview", expanded=False):
            st.text_area("Extracted Text", extracted_text[:2000], height=300)
        
        detected_lang = detect_language(extracted_text)
        st.sidebar.write(f"**Detected Language:** {detected_lang.upper()}")
        
        if st.sidebar.button("⚡ Process Extracted Text"):
            with st.spinner("Processing... Please wait."):
                try:
                    processed = asyncio.run(run_long(clean_text(extracted_text)))
                    if isinstance(processed, (dict, list)):
                        st.session_state["processed_output"] = processed
                    else:
                        st.sidebar.error("Error: Processed output is not valid JSON.")
                except Exception as e:
                    st.sidebar.error(f"An error occurred: {e}")
        
        if st.session_state["processed_output"]:
            with st.sidebar.expander("📌 Extracted Words", expanded=True):
                st.json(st.session_state["processed_output"])
            
            search_query = st.sidebar.text_input("🔎 Search in extracted words:")
            if search_query:
                filtered = {
                    key: val for key, val in st.session_state["processed_output"].items()
                    if search_query.lower() in key.lower()
                }
                st.sidebar.json(filtered)
            
            with st.sidebar.expander("📥 Download Processed Output", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📄 Download as TXT", 
                        data=download_as_text(st.session_state["processed_output"]), 
                        file_name="extracted_words.txt", 
                        mime="text/plain"
                    )
                with col2:
                    st.download_button(
                        "📂 Download as PDF", 
                        data=download_as_pdf(st.session_state["processed_output"]), 
                        file_name="extracted_words.pdf", 
                        mime="application/pdf"
                    )
        
        # ----------------------------------------
        # New: Search in PDF using run_short function
        # ----------------------------------------
        st.markdown("## Search in PDF Content ")
        search_phrase_run_short = st.text_input("Enter word or phrase to search", key="search_phrase_run_short")
        if st.button("Search ", key="search_run_short_button"):
            if not search_phrase_run_short.strip():
                st.warning("Please enter a search query.")
            else:
                with st.spinner("Searching using run_short..."):
                    try:
                        # Assuming run_short takes the full cleaned text and the search phrase as parameters.
                        search_result = asyncio.run(run_short(search_phrase_run_short))
                        st.json(search_result)
                    except Exception as e:
                        st.error(f"Error executing run_short: {e}")
    else:
        st.sidebar.warning("Please upload a file or enter a PDF URL to extract text.")

with st.sidebar.container():
    if st.sidebar.button("📂 View All Words"):
        words = get_all_words()
        if words:
            with st.sidebar.expander("All Words", expanded=True):
                for word in words:
                    st.write(f"**Word:** {word.get('word', 'Unknown')}")
                    st.write(f"**Definition:** {word.get('definition', 'No definition available')}")
                    st.write("---")
        else:
            st.sidebar.warning("No words found in the database.")

search_query_db = st.sidebar.text_input("🔎 Search Word in Database")
if search_query_db:
    word_data = search_word(search_query_db)
    if word_data:
        st.sidebar.write(f"**Word:** {word_data['word']}")
        st.sidebar.write(f"**Meaning:** {word_data['definition']}")
    else:
        st.sidebar.warning("Word not found in database.")
