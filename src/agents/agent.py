from crewai import Agent
from src.LLM.ollama_llm import ollama_llm, keyword_extractor_llm
from src.tools.tool import serper_tool

keyword_extractor = Agent(
  role='Keyword Extractor',
  goal="""Extract important keywords from the context in {language}.
          Here is the context: {context}""",
  backstory="""
    You extract key terms from the context in the same language as the context.
    These terms help students understand the topic better.
    Your work is crucial for the Researcher. 
    If the input is a single word or phrase, pass it directly to the Researcher.
  """,       # Want to see the thinking behind
  llm=ollama_llm ,
  allow_delegation=False, 
  verbose=True          # Local model
)

keyword_researcher = Agent(
  role='Keyword Researcher',
  goal='Research keywords and create definitions in {language}.',
  backstory="""
    You generate definitions in the same language as the context.
    You research keywords to help students learn more about the topic.
    If your tools do not work, you write definitions on your own.
    If the input is a single word or phrase, research only its definition and no other words.
  """,       # Want to see the thinking behind
  llm=ollama_llm,          # Using the local model
  tools=[serper_tool], 
    allow_delegation=False  
)

generate_dictionary_agent = Agent(
  role='Dictionary Generator',
  goal='Create a dictionary from keywords and definitions in {language}.',
  backstory="""
    You generate a dictionary in the same language as the context.
    Your dictionary is structured, easy to understand, and helps students learn.
  """,       # Want to see the thinking behind
  llm=ollama_llm   ,
      allow_delegation=False         # Using the local model
)