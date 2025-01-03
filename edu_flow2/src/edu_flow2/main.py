#!/usr/bin/env python
from random import randint
import os
from langtrace_python_sdk import langtrace
from pydantic import BaseModel

from crewai.flow.flow import Flow, listen, start

from .crews.edu_research2.edu_research2_crew import EduResearchCrew
from .crews.edu_content_writer2.edu_content_writer2_crew import EduContentWriterCrew
from .config import EDU_FLOW_INPUT_VARIABLES

api_key = os.getenv('LANGTRACE_API_KEY')

langtrace.init(api_key=api_key)

class EduFlow(Flow):
    input_variables = EDU_FLOW_INPUT_VARIABLES

    @start()
    def generate_reseached_content(self):
        return EduResearchCrew().crew().kickoff(self.input_variables).pydantic

    @listen(generate_reseached_content)
    def generate_educational_content(self, plan):        
        final_content = []
        for section in plan.sections:
            writer_inputs = self.input_variables.copy()
            writer_inputs['section'] = section.model_dump_json()
            final_content.append(EduContentWriterCrew().crew().kickoff(writer_inputs).raw)
        print(final_content)
        return final_content

    @listen(generate_educational_content)
    def save_to_markdown(self, content):
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        topic = self.input_variables.get("topic")
        audience_level = self.input_variables.get("audience_level")
        file_name = f"{topic}_{audience_level}.md".replace(" ", "_")
        output_path = os.path.join(output_dir, file_name)
        
        with open(output_path, "w") as f:
            for section in content:
                f.write(section)
                f.write("\n\n")
        
        # Llamar a la función para publicar en HubSpot
        self.publish_to_hubspot(output_path, topic)

    def publish_to_hubspot(self, markdown_path, title):
        import requests
        from datetime import datetime
        
        # Configuración de HubSpot
        hubspot_api_key = os.getenv('HUBSPOT_API_KEY')
        if not hubspot_api_key:
            raise ValueError("HUBSPOT_API_KEY no está configurada")
            
        # Leer el contenido del archivo markdown
        with open(markdown_path, 'r') as f:
            content = f.read()
            
        # Preparar los datos para la API de HubSpot
        blog_post = {
            "name": title,
            "contentGroupId": os.getenv('HUBSPOT_BLOG_ID'),  # ID del blog en HubSpot
            "content": content,
            "state": "DRAFT",  # o "PUBLISHED" para publicar directamente
            "publishDate": datetime.now().isoformat(),
            "blog_author": os.getenv('HUBSPOT_AUTHOR_ID'),
            "meta_description": f"Contenido educativo sobre {title}"
        }
        
        # Endpoint de la API de HubSpot
        url = "https://api.hubapi.com/cms/v3/blogs/posts"
        headers = {
            "Authorization": f"Bearer {hubspot_api_key}",
            "Content-Type": "application/json"
        }
        
        # Realizar la petición POST
        response = requests.post(url, json=blog_post, headers=headers)
        
        if response.status_code == 201:
            print(f"Post creado exitosamente en HubSpot: {title}")
        else:
            print(f"Error al crear el post: {response.status_code}")
            print(response.json())

def kickoff():
    edu_flow = EduFlow()
    edu_flow.kickoff()

def plot():
    edu_flow = EduFlow()
    edu_flow.plot()

if __name__ == "__main__":
    kickoff()
