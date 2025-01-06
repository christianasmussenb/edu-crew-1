from src.edu_flow2.llm_config import llm
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from src.edu_flow2.config import EDU_FLOW_INPUT_VARIABLES

# Uncomment the following line to use an example of a custom tool
# from edu_content_writer.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

@CrewBase
class EduContentWriterCrew():
	input_variables = EDU_FLOW_INPUT_VARIABLES
	"""EduContentWriter crew"""

	def __post_init__(self):
		self.ensure_output_folder_exists()

	def ensure_output_folder_exists(self):
		"""Ensure the output folder exists."""
		output_folder = 'output'
		if not os.path.exists(output_folder):
			os.makedirs(output_folder)

	@agent
	def content_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['content_writer'],
			llm=llm,
			verbose=False
		)

	@agent
	def editor(self) -> Agent:
		return Agent(
			config=self.agents_config['editor'],
			llm=llm,
			verbose=False
		)

	@agent
	def quality_reviewer(self) -> Agent:
		return Agent(
			config=self.agents_config['quality_reviewer'],
			llm=llm,
			verbose=False
		)
	
	@agent
	def blog_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['blog_writer'],
			llm=llm,
			verbose=True
		)
	
	@task
	def writing_task(self) -> Task:
		return Task(
			config=self.tasks_config['writing_task'],
		)

	@task
	def editing_task(self) -> Task:
		topic = self.input_variables.get("topic")
		audience_level = self.input_variables.get("audience_level")
		file_name = f"{topic}_{audience_level}.md".replace(" ", "_")
		output_file_path = os.path.join('output', file_name)
		
		return Task(
			config=self.tasks_config['editing_task'],
			output_file=output_file_path
		)

	@task
	def quality_review_task(self) -> Task:
		return Task(
			config=self.tasks_config['quality_review_task'],
		)

	@task
	def blog_formatting_task(self) -> Task:
		topic = self.input_variables.get("topic")
		audience_level = self.input_variables.get("audience_level")
		file_name = f"{topic}_{audience_level}_blob.md".replace(" ", "_")
		blob_file_path = os.path.join('output', file_name)
		
		return Task(
			config=self.tasks_config['blog_formatting_task'],
			output_file=blob_file_path
		)
	
	@crew
	def crew(self) -> Crew:
		"""Creates the EduContentWriter crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=False,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
