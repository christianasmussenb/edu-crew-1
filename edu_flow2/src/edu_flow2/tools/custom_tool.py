from typing import Type
from crewai_tools import BaseTool
import hubspot.client
from pydantic import BaseModel, Field
import hubspot
from hubspot.cms.blogs.blog_posts import BlogPost, ApiException
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Blog(BaseModel):
    """Modelo para la entrada del blog."""
    titulo: str = Field(..., description="Título del post")
    descripcion: str = Field(..., description="Descripción del post")
    cuerpo: str = Field(..., description="Cuerpo del post")
    imagen: str = Field(..., description="URL de la imagen del post")

class HubSpotPostTool(BaseTool):
    name: str = "HubSpot Blog Post Tool"
    description: str = (
        "Posts content to HubSpot blogs. Can post to different blogs based on configuration."
    )
    args_schema: Type[BaseModel] = Blog

    def create_blog_post(self, client: hubspot.client.Client, blog: Blog, content_group_id: str, blog_author_id: str) -> str:
        """Crea un post de blog individual a partir de un objeto Blog."""
        blog_post = {
            "name": blog.titulo,
            "htmlTitle": blog.titulo,
            "contentGroupId": content_group_id,
            "content": " ",
            "state": "DRAFT",
            "language": "es-cl",
            "blogAuthorId": blog_author_id,
            "slug": f"blog/{blog.titulo}",
            "metaDescription": blog.descripcion,
            "postBody": f"""
            <img src="{blog.imagen}" 
                alt="{blog.titulo}" style="width:50%; max-width:800px; margin: 20px auto; display:block;">
            {blog.cuerpo.strip()}
            """,
            "postSummary": f"<p>{blog.descripcion}</p>",
            "rssBody": blog.cuerpo.strip(),
            "rssSummary": f"<p>{blog.descripcion}</p>",
            "featuredImage": blog.imagen,
            "featuredImageAltText": blog.titulo,
            "currentlyPublished": False,
            "publicAccessRulesEnabled": False,
            "publishImmediately": False,
            "publishDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        try:
            api_response = client.cms.blogs.blog_posts.blog_post_api.create(blog_post=blog_post)
            return f"✅ Post creado exitosamente: {blog.titulo}"
        except ApiException as e:
            return f"❌ Error al crear el post: {str(e)}"
        except Exception as e:
            return f"❌ Error inesperado: {str(e)}"

    def _run(self, blog: Blog, content_group_id: str, blog_author_id: str, access_token: str) -> str:
        """Ejecuta la herramienta con el objeto Blog y las credenciales necesarias."""
        try:
            client: hubspot.client.Client = hubspot.client.Client.create(access_token=access_token)
            return self.create_blog_post(client, blog, content_group_id, blog_author_id)
        except Exception as e:
            return f"Error al ejecutar la herramienta: {str(e)}"
