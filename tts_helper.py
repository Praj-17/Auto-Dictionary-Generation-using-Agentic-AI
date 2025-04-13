import os
import uuid
import base64
import time
import soundfile as sf
from io import BytesIO
import numpy as np
from kokoro import KPipeline
from src.helpers import chunk_text

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
        yielding WAV filenames as partial chunks are ready.
        """
        generator = self.pipeline(text, voice=self.voice, speed=0.8)
        for i, (_, _, audio) in enumerate(generator):
            output_filename = f'{self.output_dir}/{uuid.uuid4()}.wav'
            sf.write(output_filename, audio, 24000)
            yield output_filename

def stream_text_to_speech(text, lang="es", voice="af_heart", chunk_size=300):
    """
    Splits the input text into smaller chunks and processes each chunk with TTS.
    The first yielded chunk includes the full WAV header and subsequent chunks have the 44-byte header stripped.
    Chunks are yielded one-by-one so the frontend can append them to the audio player.
    """
    chunks = chunk_text(text, max_chars=chunk_size)
    first_chunk = True

    for chunk in chunks:
        tts_generator = KokoroTTSGenerator(lang_code=lang, voice=voice)
        for file_path in tts_generator.generate_audio(chunk):
            with open(file_path, "rb") as f:
                data = f.read()
            os.remove(file_path)
            # Remove the WAV header (first 44 bytes) for subsequent chunks.
            if not first_chunk:
                data = data[44:]
            else:
                first_chunk = False
            yield data
