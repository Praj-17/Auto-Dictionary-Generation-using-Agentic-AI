from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
load_dotenv()
import os

# Keyword Extractor agent
keyword_extractor_llm = OllamaLLM(
    model=os.environ.get("KEYWORD_EXTRACTOR_MODEL", "ollama/qwen2:0.5b"),
    base_url=os.environ.get("API_BASE", "http://ollama:11434"),
)

# Keyword Researcher agent
keyword_researcher_llm = OllamaLLM(
    model=os.environ.get("KEYWORD_RESEARCHER_MODEL", "MiniCPM"),
    base_url=os.environ.get("API_BASE", "http://ollama:11434")
)

# Dictionary Generator agent
dictionary_generator_llm = OllamaLLM(
    model=os.environ.get("DICTIONARY_GENERATOR_MODEL", "ollama/qwen2:0.5b"),
    base_url=os.environ.get("API_BASE", "http://ollama:11434"),
)


ollama_llm = OllamaLLM(
    model=os.environ.get("MODEL", "ollama/qwen2:0.5b"),
    base_url=os.environ.get("API_BASE", "http://ollama:11434"),
)

# Check if the model is running by invoking it with a simple prompt
try:
    response = ollama_llm.invoke("Hello, are you running?")
    print("Model Response:", response)
except Exception as e:
    print("Error invoking the model:", e)


# Debug prints
print("Keyword Extractor LLM:", ollama_llm.model)