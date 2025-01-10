#!/usr/bin/env python

import os
from pydantic import BaseModel

from crewai.flow.flow import Flow, listen, start

from edu_flow2.crews.edu_research2.edu_research2_crew import EduResearchCrew
from edu_flow2.crews.edu_content_writer2.edu_content_writer2_crew import EduContentWriterCrew
from edu_flow2.config import EDU_FLOW_INPUT_VARIABLES

#from .test_hubspot_post import publish_to_hubspot

from langtrace_python_sdk import langtrace
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
            #writer_inputs['blog'] = blog
            final_content.append(EduContentWriterCrew().crew().kickoff(writer_inputs).raw)
        #print(final_content)
        return final_content

    @listen(generate_educational_content)
    def save_to_markdown(self, content):
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        topic = self.input_variables.get("topic")
        audience_level = self.input_variables.get("audience_level")
        base_file_name = f"{topic}_{audience_level}".replace(" ", "_")
        
        # Guardar cada sección en un archivo separado
        for index, section in enumerate(content, 1):
            file_name = f"{base_file_name}_section_{index}.md"
            output_path = os.path.join(output_dir, file_name)
            
            with open(output_path, "w") as f:
                f.write(section)
            
                #publish_to_hubspot(output_path)
                print(f"✅ Sección {index} guardada en: {output_path}")

def process_content(input_vars):
    edu_flow = EduFlow()
    edu_flow.input_variables = input_vars
    return edu_flow.kickoff()

def kickoff():
    edu_flow = EduFlow()
    edu_flow.kickoff()

def plot():
    edu_flow = EduFlow()
    edu_flow.plot()

if __name__ == "__main__":
    kickoff()
