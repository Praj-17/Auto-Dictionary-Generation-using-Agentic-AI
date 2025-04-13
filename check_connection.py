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

# Import helper functions from tts_helper.py and others
from tts_helper import stream_text_to_speech  # Our updated streaming TTS function
from src.helpers import (
    extract_text_from_file,
    extract_text_from_pdf_url,
    detect_language,
    translate_text,
    download_as_text,
    download_as_pdf
)
from src.utils.split_text import clean_text
from pypdf import PdfReader
from io import BytesIO
from fpdf import FPDF
from main import run_long, run_short  # If defined elsewhere in your codebase
from src.database import get_all_words, search_word  # Import MongoDB functions

# -----------------------------
# Helper: Language Mapping Function
# -----------------------------
def map_language(lang_code):
    """
    Map detected language (e.g. 'en', 'es', etc.) to a corresponding short TTS code:
    
    🇺🇸 'a' => American English (default if 'en')
    🇬🇧 'b' => British English
    🇪🇸 'e' => Spanish
    🇫🇷 'f' => French
    🇮🇳 'h' => Hindi
    🇮🇹 'i' => Italian
    🇯🇵 'j' => Japanese
    🇧🇷 'p' => Brazilian Portuguese
    🇨🇳 'z' => Mandarin Chinese
    """
    lang = lang_code.lower()
    if lang.startswith("en"):
        return "a"  # Defaulting to American English; adjust if needed.
    elif lang.startswith("es"):
        return "e"
    elif lang.startswith("fr"):
        return "f"
    elif lang.startswith("hi"):
        return "h"
    elif lang.startswith("it"):
        return "i"
    elif lang.startswith("ja"):
        return "j"
    elif lang.startswith("pt"):
        return "p"
    elif lang.startswith("zh"):
        return "z"
    else:
        return "a"

# -----------------------------
# Custom Audio Player Component
# -----------------------------
def render_audio_player():
    """
    Renders a custom audio player using the MediaSource API.
    
    The audio player exposes a global JavaScript function, `window.appendAudioChunk`,
    which appends new audio data (provided as a base64 string) to the player's
    SourceBuffer without restarting playback.
    """
    player_html = r"""
    <html>
      <head>
        <meta charset="utf-8">
      </head>
      <body>
        <audio id="audioPlayer" controls autoplay></audio>
        <script>
          const audio = document.getElementById('audioPlayer');
          const mediaSource = new MediaSource();
          audio.src = URL.createObjectURL(mediaSource);
          let sourceBuffer;
          mediaSource.addEventListener('sourceopen', function() {
              try {
                  // The codec here is set to audio/wav; adjust if needed.
                  sourceBuffer = mediaSource.addSourceBuffer('audio/wav');
              } catch(e) {
                  console.error('Error creating SourceBuffer:', e);
              }
          });
          
          // Global function to append audio chunk (a base64-encoded string)
          window.appendAudioChunk = function(chunkBase64) {
              let binary_string = window.atob(chunkBase64);
              let len = binary_string.length;
              let bytes = new Uint8Array(len);
              for (let i = 0; i < len; i++) {
                  bytes[i] = binary_string.charCodeAt(i);
              }
              let audioData = bytes.buffer;
              if (sourceBuffer.updating) {
                  setTimeout(() => { window.appendAudioChunk(chunkBase64); }, 100);
              } else {
                  try {
                      sourceBuffer.appendBuffer(audioData);
                  } catch (e) {
                      console.error("Error appending audio:", e);
                  }
              }
          };
        </script>
      </body>
    </html>
    """
    st.components.v1.html(player_html, height=250)

# -----------------------------
# Environment and Warning Configurations
# -----------------------------
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"
torch.classes.__path__ = []
warnings.filterwarnings("ignore", message="<built-in function callable> is not a Python type")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.nn.utils.weight_norm")

# Set page title and layout
st.set_page_config(page_title="Autodictionary", layout="wide")

if "processed_output" not in st.session_state:
    st.session_state["processed_output"] = None

# -----------------------------
# Custom CSS for UI Styling
# -----------------------------
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

# -----------------------------
# Sidebar: File Upload & PDF URL Input
# -----------------------------
st.sidebar.header("Upload & PDF URL")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or TXT files", 
    type=["pdf", "txt"], 
    accept_multiple_files=True
)
st.sidebar.subheader("Extract from PDF URL")
pdf_url_input = st.sidebar.text_input("Enter the URL of a research paper PDF:")

# -----------------------------
# Main File Viewer & Listen Feature (Streaming TTS)
# -----------------------------
if uploaded_files:
    st.header("📂 File Viewer")
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type
        file_name = uploaded_file.name
        st.subheader(f"File: {file_name}")
        
        # --- Audio Controls Container (on top) ---
        with st.container():
            if st.button("🔊 Listen Full Audio", key=f"{file_name}_listen_full"):
                try:
                    # Render the audio player above the file view.
                    render_audio_player()
                    
                    # Extract text from the file for TTS processing.
                    if file_type == "application/pdf":
                        uploaded_file.seek(0)
                        pdf_reader = PdfReader(uploaded_file)
                        text_content = ""
                        for page in pdf_reader.pages:
                            page_text = page.extract_text() or ""
                            text_content += page_text + "\n"
                    elif file_type == "text/plain":
                        uploaded_file.seek(0)
                        text_content = uploaded_file.read().decode("utf-8")
                    
                    if not text_content.strip():
                        st.warning("No extractable text found for speech.")
                    else:
                        detected = detect_language(text_content)
                        tts_lang = map_language(detected)
                        st.info("Streaming audio... please do not refresh the page.")
                        script_placeholder = st.empty()  # For injecting JS chunks.
                        
                        # Stream audio chunks; note that each chunk (after the first) is a new segment.
                        for chunk_bytes in stream_text_to_speech(text_content, lang=tts_lang):
                            chunk_b64 = base64.b64encode(chunk_bytes).decode('utf-8')
                            script = f"<script>window.appendAudioChunk('{chunk_b64}');</script>"
                            script_placeholder.markdown(script, unsafe_allow_html=True)
                            # A slight delay to pace the updates (adjust as needed)
                            time.sleep(0.5)
                        st.success("Audio streaming complete!")
                except Exception as e:
                    st.error(f"Text-to-speech error: {e}")
        
        # --- File Viewer Container (always visible) ---
        with st.container():
            if file_type == "application/pdf":
                uploaded_file.seek(0)
                with st.expander("View PDF", expanded=True):
                    pdf_viewer(uploaded_file.getvalue(), width=1000, height=1000)
            elif file_type == "text/plain":
                uploaded_file.seek(0)
                text_content = uploaded_file.read().decode("utf-8")
                with st.expander("View File Content", expanded=True):
                    st.text_area("Content", text_content, height=600)

elif pdf_url_input:
    st.info("🔄 Downloading & Extracting text from PDF URL...")
    text_from_url = extract_text_from_pdf_url(pdf_url_input)
    st.header("📄 PDF Content from URL")
    
    # --- Audio Controls Container (on top) ---
    with st.container():
        if st.button("🔊 Listen Full Audio (URL)", key="url_listen_full"):
            if not text_from_url.strip():
                st.warning("No extractable text found from PDF URL.")
            else:
                try:
                    detected = detect_language(text_from_url)
                    tts_lang = map_language(detected)
                    st.info("Streaming audio... please do not refresh the page.")
                    render_audio_player()  # Render audio player upon clicking.
                    script_placeholder = st.empty()
                    for chunk_bytes in stream_text_to_speech(text_from_url, lang=tts_lang):
                        chunk_b64 = base64.b64encode(chunk_bytes).decode('utf-8')
                        script = f"<script>window.appendAudioChunk('{chunk_b64}');</script>"
                        script_placeholder.markdown(script, unsafe_allow_html=True)
                        time.sleep(0.5)
                    st.success("Audio streaming complete!")
                except Exception as e:
                    st.error(f"Text-to-speech error: {e}")
    
    # --- File Viewer Container (always visible) ---
    with st.container():
        with st.expander("View PDF Extracted Text", expanded=True):
            st.text_area("Extracted Text", text_from_url, height=600)
else:
    st.info("Please upload a file or enter a PDF URL to extract and view content.")

# -----------------------------
# Sidebar: Process Extracted Text & Database Tools
# -----------------------------
with st.sidebar.container():
    if uploaded_files or pdf_url_input:
        extracted_text = extract_text_from_file(uploaded_files) if uploaded_files else text_from_url
        with st.sidebar.expander("📜 Extracted Text Preview", expanded=False):
            st.text_area("Extracted Text", extracted_text[:2000], height=300)
        
        detected_lang = detect_language(extracted_text)
        st.sidebar.write(f"**Detected Language:** `{detected_lang.upper()}`")
        
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
