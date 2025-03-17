from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
load_dotenv()
import os
ollama_llm = OllamaLLM(model=os.getenv("MODEL"), base_url=os.getenv("API_BASE"))
