from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.auto_dict.models.models import Dictionary
from crewai_tools import (
  SerperDevTool
)


from dotenv import load_dotenv

load_dotenv()



# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
search_tool = SerperDevTool()
@CrewBase
class AutoDict():
	"""AutoDict crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def keyword_extractor(self) -> Agent:
		return Agent(
			config=self.agents_config['keyword_extractor'],
			verbose=True
		)

	# @agent
	# def critic_agent(self) -> Agent:
	# 	return Agent(
	# 		config=self.agents_config['critic_agent'],
	# 		verbose=False
	# 	)

	@agent
	def keyword_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['keyword_researcher'],
			verbose=False
			
		)

	@agent
	def generate_dictionary_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['generate_dictionary_agent'],
			verbose=True
			
		)
	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task']
		)
	
	@task
	def keyword_task(self) -> Task:
		return Task(
			config=self.tasks_config['keyword_task'],
			verbose=True,

		)



	@task
	def generate_dictionary_task(self) -> Task:
		return Task(
			config=self.tasks_config['generate_dictionary_task'],
			verbose=True
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the AutoDict crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			planning=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
