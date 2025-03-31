from crewai import Agent
from src.LLM.ollama import ollama_llm
from src.tools.tool import serper_tool


keyword_extractor = Agent(
  role='Keyword Extractor',
  goal="""     Extract important keywords from the context.
      Here is the context: {context}""",
  backstory="""
    You extract key terms from the context in the same language.
    These terms help students understand the topic better.
    Your work is crucial for the Researcher. 
    if it is a single word or phrase pass it directly to the Researcher
  """,
  verbose=True,            # want to see the thinking behind# Not allowed to ask any of the other roles
  llm=ollama_llm           # local model
)


keyword_researcher = Agent(
  role='Keyword Researcher',
  goal=' Research keywords and create definitions.',
  backstory="""You generate definitions in the same language as the context.
    You research keywords to help students learn more about the topic.
    If your tools do not work you write definations on its own.""",
  verbose=True,            # want to see the thinking behind# can ask the "researcher" for more information
  llm=ollama_llm  ,          # using the local model
  tools=[serper_tool]
)


generate_dictionary_agent = Agent(
  role='Dictionary Generator',
  goal=' Create a dictionary from keywords and definitions..',
  backstory=""" You generate a dictionary in the same language as the context.
    Your dictionary is structured, easy to understand, and helps students learn""",
  verbose=True,            # want to see the thinking behind
  llm=ollama_llm           # using the local model
)