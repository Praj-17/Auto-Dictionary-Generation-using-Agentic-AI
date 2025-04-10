import os
import requests
from langchain.agents import Agent, Tool 
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the Serper API logic
def search_with_serper(query):
    api_key = "YOUR_SERPER_API_KEY"
    api_url = "https://serper.com/api"

    params = {
        "q": query,
        "location": "United States",
        "google_domain": "google.com",
        "num": 10,
        "start": 0,
        "api_key": api_key
    }

    try:
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            results = []

            for result in data["organic_results"]:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")

                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })

            return results
        else:
            print(f"Failed to retrieve results. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def extract_definitions_with_serper(query):
    results = search_with_serper(query)

    definitions = []

    for result in results:
        snippet = result["snippet"]
        definition = snippet.split(".")[0] if snippet else ""

        definitions.append({
            "keyword": query,
            "definition": definition
        })

    return definitions

# Define the Serper tool
serper_tool = Tool(
    name="Serper Search",
    func=extract_definitions_with_serper,
    description="Search tool powered by Serper API for definition extraction"
)

# Initialize the Ollama model
ollama_llm = OllamaLLM(
    model=os.environ.get("MODEL", "ollama/qwen2:0.5b"),
    base_url=os.environ.get("API_BASE", "http://ollama:11434")
)

# Create the keyword researcher agent
keyword_researcher = Agent(
    role='Keyword Researcher',
    goal='Research keywords and create definitions in {language}.',
    backstory="""
        You generate definitions in the same language as the context.
        You research keywords to help students learn more about the topic.
        If your tools do not work, you write definitions on your own.
        If the input is a single word or phrase, research only its definition and no other words.
    """,
    llm=ollama_llm,          # Using the local model
    tools=[serper_tool], 
    allow_delegation=False  
)

# Define the research task
# research_task = Task(
#     agent=keyword_researcher,
#     description= """  
#         1. Research the extracted keywords online.
#         2. Define each keyword with an example.
#         3. Determine the correct POS tag.
#         4. Avoid redundancy.
#         5. Keep keywords in the original language.
#         6. If the input is a single word or phrase, research only its definition, etc., without adding other words.
#         7. Strictly do not research any new or related words, only find definitions for the given keywords.
        
#         POS Tag should be one of these:

#         ADJ = "ADJ"  # Adjective
#         ADP = "ADP"  # Adposition (preposition, postposition, etc.)
#         ADV = "ADV"  # Adverb
#         AUX = "AUX"  # Auxiliary verb
#         CCONJ = "CCONJ"  # Coordinating conjunction
#         DET = "DET"  # Determiner
#         INTJ = "INTJ"  # Interjection
#         NOUN = "NOUN"  # Noun
#         NUM = "NUM"  # Numeral
#         PART = "PART"  # Particle
#         PRON = "PRON"  # Pronoun
#         PROPN = "PROPN"  # Proper noun
#         PUNCT = "PUNCT"  # Punctuation
#         SCONJ = "SCONJ"  # Subordinating conjunction
#         SYM = "SYM"  # Symbol
#         VERB = "VERB"  # Verb
#         X = "X"  # Other
#     """,
#     expected_output=" A structured list of keywords with definitions in {language}."
# )

# Example usage
keywords = ["Artificial Intelligence", "Machine Learning"]
research_task.input = {"keywords": keywords}

# Run the task
try:
    result = keyword_researcher.run(research_task)
    print(result)
except Exception as e:
    print("Error running the task:", e)
