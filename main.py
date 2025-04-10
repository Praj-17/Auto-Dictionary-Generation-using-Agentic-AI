import os
import asyncio
from dotenv import load_dotenv
from src.utils.split_text import chunk_text, clean_text
from src.utils.to_pydantic import TextToPydanticConverter
from src.crew import auto_dict_crew
from src.models.models import Dictionary
from src.database import save_word
from src.kokoro_tts import KokoroTTSGenerator
from src.utils.detect_lang import detect_language_full_name
from crewai.crew import CrewOutput
import warnings
import json

# Create the /logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set environment variable for Streamlit
os.environ["STREAMLIT_WATCH_FOR_CHANGES"] = "false"

# Define a regular expression for the module(s) you want to target
IGNORE_MODULES = 'crewai|src|pydantic|json|asyncio|re|warnings'

# Apply the filter to ignore deprecation warnings from the specified modules
warnings.filterwarnings("ignore", category=DeprecationWarning, module=IGNORE_MODULES)

load_dotenv()

to_pydantic = TextToPydanticConverter()
tts_generator = KokoroTTSGenerator()

async def process_chunk(input_dict):
    """
    Processes a single chunk.
    """
    try:
        result = await auto_dict_crew.kickoff_async(inputs=input_dict)
        if isinstance(result, CrewOutput):
            # Convert the result to a Pydantic model
                raw_data = result.model_dump().get("raw")
                raw_data = raw_data.replace("json", "").strip("```")
                if isinstance(raw_data, str):
                    try:
                        raw_dict = Dictionary.model_validate_json(raw_data)
                        return raw_dict.model_dump()
                    except json.JSONDecodeError as e:
                        raw_dict = {}
                        return raw_dict
                else:
                    raw_dict = {}
                    return raw_dict
        elif isinstance(result, Dictionary):
            return result
    except Exception as e:
        pass
    return {}

async def run_long(text, batch_size=10):
    """
    Processes a long text by splitting it into chunks and processing each chunk asynchronously.
    """
    chunks = chunk_text(text)
    language = detect_language_full_name(text)
    inputs = [{"context": chunk, "retry_count": 0, "language": language} for chunk in chunks]

    final_results = []
    tasks = []
    for input_dict in inputs:
        tasks.append(process_chunk(input_dict))
        if len(tasks) >= batch_size:
            results = await asyncio.gather(*tasks)
            final_results.extend([res for res in results if res])
            tasks = []

    # Process any remaining tasks
    if tasks:
        results = await asyncio.gather(*tasks)
        final_results.extend([res.get('entries') for res in results if res])

    return final_results

async def run_short(word):
    """
    Processes a single word or phrase to get its meaning.
    """
    language = detect_language_full_name(word)
    cleaned_word = clean_text(word)
    input_dict = {"context": cleaned_word, "retry_count": 0, "language": language}
    try:
        result = await process_chunk(input_dict)
        if result:
            return result
    except Exception as e:
        pass
    return {}

if __name__ == "__main__":
    text = """Las aves son animales vertebrados que se caracterizan por tener plumas, alas y pico. La mayoría de las aves pueden volar, aunque algunas especies, como el pingüino o el avestruz, no lo hacen. Viven en diversos hábitats alrededor del mundo y desempeñan un papel importante en los ecosistemas, ayudando en la polinización, el control de insectos y la dispersión de semillas. Además, su canto y colorido plumaje las hacen fascinantes para muchas personas."""

    output = asyncio.run(run_long(clean_text(text)))

    if isinstance(output, dict) or isinstance(output, list):
        with open("outputs/output_spanish_4.json", "w") as f:
            json.dump(output, f, indent=4)
