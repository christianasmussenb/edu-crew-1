from edu_flow2.tools.custom_tool import Blog, HubSpotPostTool
import os
from dotenv import load_dotenv

load_dotenv()
# Definición de las variables necesarias
content_group_id = os.getenv("OTRA_HUBSPOT_BLOG_ID")
blog_author_id = os.getenv("OTRA_HUBSPOT_AUTHOR_ID")
access_token = os.getenv("OTRA_HUBSPOT_API_KEY")

# Creación de un objeto Blog
blog = Blog(
    titulo="Título del Post",
    descripcion="Descripción del Post",
    cuerpo="Cuerpo del Post Otra Cuerpo",
    imagen="https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/1_edICTq8-DfLxpOJE38hEmA.jpeg"
)

# Crear una instancia de HubSpotPostTool
tool_instance = HubSpotPostTool()

# Llamada al método _run
resultado = tool_instance._run(blog, content_group_id, blog_author_id, access_token)

print(resultado) 