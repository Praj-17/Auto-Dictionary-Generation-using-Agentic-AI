from src.agents.agent import keyword_extractor, keyword_researcher, generate_dictionary_agent
from src.tasks.tasks import keyword_task, research_task, generate_dictionary_task
from crewai import Crew


auto_dict_crew = Crew(
  agents=[keyword_extractor, keyword_researcher, generate_dictionary_agent],
  tasks=[keyword_task, research_task, generate_dictionary_task],
  verbose = 1
)

