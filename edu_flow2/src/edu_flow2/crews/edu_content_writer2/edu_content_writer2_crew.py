from src.edu_flow2.llm_config import llm
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from src.edu_flow2.config import EDU_FLOW_INPUT_VARIABLES
#from src.edu_flow2.tools.custom_tool import HubSpotPostTool, Blog
#from pydantic import BaseModel, Field
#from typing import Type

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
			verbose=True,
			#tools=[HubSpotPostTool()],
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
		file_name = f"{topic}_{audience_level}_blog.md".replace(" ", "_")
		blog_file_path = os.path.join('output', file_name)
		
		return Task(
			config=self.tasks_config['blog_formatting_task'],
			output_file=blog_file_path
		)

	"""	
	@task
	def hubspot_posting_task(self) -> Task:
		topic = self.input_variables.get("topic")
		audience_level = self.input_variables.get("audience_level")
		file_name = f"{topic}_{audience_level}_blog.md".replace(" ", "_")
		blog_file_path = os.path.join('output', file_name)
		content_group_id = os.getenv("OTRA_HUBSPOT_BLOG_ID")
		blog_author_id = os.getenv("OTRA_HUBSPOT_AUTHOR_ID")
		access_token = os.getenv("OTRA_HUBSPOT_API_KEY")
		hubspot_tool = HubSpotPostTool()
		return Task(
			config=self.tasks_config['hubspot_posting_task'],
			tools=[hubspot_tool(blog_file_path, content_group_id, blog_author_id, access_token)],
			context={
				"blog_file": blog_file_path,  # Pasar el path del archivo blog
			#	"content_group_id": content_group_id,
			#	"blog_author_id": blog_author_id,
			#	"access_token": access_token,
			}
		)
		"""

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
