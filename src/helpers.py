import os
import json
import uuid
from io import BytesIO
import requests
from pypdf import PdfReader
from fpdf import FPDF
from langdetect import detect
from googletrans import Translator
import numpy as np
import threading
import queue
import soundfile as sf
import re

# --- Kokoro TTS Imports and Class Definition ---
from kokoro import KPipeline

translator = Translator()

def extract_text_from_file(files):
    """
    Extract text from uploaded files (plain text and PDF).
    """
    extracted_texts = []
    for uploaded_file in files:
        if uploaded_file.type == "text/plain":
            extracted_texts.append(uploaded_file.read().decode("utf-8"))
            uploaded_file.seek(0)
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            extracted_texts.append(text)
            uploaded_file.seek(0)
    return "\n\n".join(extracted_texts)

def extract_text_from_pdf_url(pdf_url):
    """
    Download a PDF from a URL and extract its text.
    """
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
        temp_pdf_path = "temp_research_paper.pdf"
        with open(temp_pdf_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)
        pdf_reader = PdfReader(temp_pdf_path)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        os.remove(temp_pdf_path)
        return text if text else "No readable text found in the PDF."
    except requests.exceptions.RequestException as e:
        return f"Error downloading PDF: {e}"
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

def detect_language(text):
    """
    Detect the language of the given text.
    """
    try:
        return detect(text)
    except Exception:
        return "Unknown"

def translate_text(text, target_lang="en"):
    """
    Translate text to a target language (default is English).
    """
    try:
        return translator.translate(text, dest=target_lang).text
    except Exception:
        return "Translation failed."

def download_as_text(data):
    """
    Convert JSON data to a text file for download.
    """
    return BytesIO(json.dumps(data, indent=4).encode("utf-8"))

def download_as_pdf(data):
    """
    Convert JSON data to a PDF document for download.
    """
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

def chunk_text(text, max_chars=300):
    """
    Splits 'text' into smaller pieces of up to 'max_chars' characters each.
    This ensures we get multiple partial TTS results rather than one big chunk.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

class KokoroTTSGenerator:
    def __init__(self, lang_code='es', voice='af_heart', output_dir='src/output/kokoro'):
        self.pipeline = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')
        self.voice = voice
        self.output_dir = output_dir
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def generate_audio(self, text):
        """
        Synthesize the given text with the Kokoro pipeline,
        yielding WAV filenames as soon as partial audio segments are ready.
        """
        generator = self.pipeline(text, voice=self.voice, speed=0.8)
        for i, (_, _, audio) in enumerate(generator):
            output_filename = f'{self.output_dir}/{uuid.uuid4()}.wav'
            sf.write(output_filename, audio, 24000)
            yield output_filename

def _generate_chunk_async(chunk, lang, voice):
    """
    Worker function to process a single chunk asynchronously.
    Generates audio using a new KokoroTTSGenerator instance and puts results into a queue.
    """
    q = queue.Queue()
    def worker():
        tts_gen = KokoroTTSGenerator(lang_code=lang, voice=voice)
        for file_path in tts_gen.generate_audio(chunk):
            with open(file_path, "rb") as f:
                data = f.read()
            os.remove(file_path)
            q.put(data)
        q.put(None)  # Signal completion
    threading.Thread(target=worker, daemon=True).start()
    return q

def stream_text_to_speech(text, lang="es", voice="af_heart", chunk_size=300):
    """
    Splits the text into smaller chunks and processes each chunk concurrently.
    The first chunk yields a full WAV file (including header). Subsequent chunks have their
    44-byte header stripped, so that when concatenated in the frontend the audio plays seamlessly.
    """
    chunks = chunk_text(text, max_chars=chunk_size)
    # Start all chunk tasks concurrently and store their queues in order.
    tasks = [ _generate_chunk_async(chunk, lang, voice) for chunk in chunks ]
    # Process each chunk’s queue sequentially to ensure correct order.
    for idx, q in enumerate(tasks):
        while True:
            data = q.get()
            if data is None:
                break
            # For subsequent chunks, strip off the header.
            if idx > 0:
                data = data[44:]
            yield data
