from src.agents.agent import keyword_extractor, keyword_researcher, generate_dictionary_agent, keyword_researcher_single
from src.tasks.tasks import keyword_task, research_task, generate_dictionary_task, research_task_single
from crewai import Crew


auto_dict_crew = Crew(
  agents=[keyword_extractor, keyword_researcher, generate_dictionary_agent],
  tasks=[keyword_task, research_task, generate_dictionary_task],
  verbose = 1
)

auto_dict_crew_single = Crew(
    agents = [keyword_researcher_single, generate_dictionary_agent], 
    tasks = [research_task_single, generate_dictionary_task],
    verbose = 1, 
)

