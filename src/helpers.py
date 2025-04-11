import os
import json
import uuid
from io import BytesIO
import requests
from pypdf import PdfReader
from fpdf import FPDF
from langdetect import detect
from googletrans import Translator

# --- Kokoro TTS Imports and Class Definition ---
from kokoro import KPipeline
import soundfile as sf

class KokoroTTSGenerator:
    def __init__(self, lang_code='es', voice='af_heart', output_dir='src/output/kokoro'):
        self.pipeline = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')
        self.voice = voice
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def generate_audio(self, text):
        generator = self.pipeline(text, voice=self.voice, speed=0.8)
        
        for i, (gs, ps, audio) in enumerate(generator):
            # Generate a unique filename using UUID
            output_filename = f'{self.output_dir}/{uuid.uuid4()}.wav'
            
            # Save the audio to a WAV file
            sf.write(output_filename, audio, 24000)
            
            # Yield the filename (or audio data) for further use
            yield output_filename

# --- Other Helper Functions (extraction, downloading, etc.) ---

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

def text_to_speech(text, lang="es", voice="af_heart"):
    """
    Convert text to speech using the KokoroTTSGenerator.
    Returns a BytesIO object containing the WAV audio data.
    
    Note: The default language is set to Spanish ('es') and the default voice to 'af_heart'.
    Adjust these parameters as needed.
    """
    tts_generator = KokoroTTSGenerator(lang_code=lang, voice=voice)
    # Retrieve the first generated audio file
    file_path = next(tts_generator.generate_audio(text))
    
    # Read the file data into a BytesIO object
    with open(file_path, "rb") as f:
         audio_data = f.read()
    
    # Optionally, delete the temporary file if no longer needed:
    # os.remove(file_path)
    
    return BytesIO(audio_data)
