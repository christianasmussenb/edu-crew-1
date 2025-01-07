from typing import Type
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import hubspot
from hubspot.cms.blogs.blog_posts import BlogPost, ApiException
from datetime import datetime
import os
from dotenv import load_dotenv
import re

load_dotenv()

class HubSpotPostInput(BaseModel):
    """Input schema for HubSpotPostTool."""
    markdown_path: str = Field(..., description="Path to the markdown file to be posted")
    is_second_blog: bool = Field(False, description="Whether to post to the second blog")

class HubSpotPostTool(BaseTool):
    name: str = "HubSpot Blog Post Tool"
    description: str = (
        "Posts content to HubSpot blogs. Can post to two different blogs based on configuration. "
        "Requires markdown_path and optionally is_second_blog parameter."
    )
    args_schema: Type[BaseModel] = HubSpotPostInput

    def create_blog_post(self, client, content, index, is_second_execution=False):
        """Crea un post de blog individual"""
        # Buscar el título en el tag <h1>
        title_match = re.search(r'<h1>(.*?)</h1>', content)
        if title_match:
            title = title_match.group(1)
        else:
            # Buscar en el tag <title> como respaldo
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                title = title_match.group(1)
            else:
                # Si no se encuentra título, usar uno por defecto
                title = f"Part {index} - AI Content"
        
        # Limitar longitud del título
        title = title[:60]
        
        # Limpiar el contenido - remover tags html, head y body
        content = re.sub(r'<!DOCTYPE.*?>', '', content, flags=re.DOTALL)
        content = re.sub(r'<html.*?>', '', content, flags=re.DOTALL)
        content = re.sub(r'</html>', '', content)
        content = re.sub(r'<head>.*?</head>', '', content, flags=re.DOTALL)
        content = re.sub(r'<body>|</body>', '', content)
        
        # Seleccionar configuración según la ejecución
        if not is_second_execution:
            images = [
                "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/1_edICTq8-DfLxpOJE38hEmA.jpeg",
                "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/pexels-photo-3313333.jpg",
                "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/AdobeStock_409843373-1.jpeg",
                "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/pexels-photo-3313333.jpg",
                "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/1_edICTq8-DfLxpOJE38hEmA.jpeg"
            ]
            content_group_id = os.getenv('HUBSPOT_BLOG_ID')
            blog_author_id = os.getenv('HUBSPOT_AUTHOR_ID')
        else:
            images = [
                "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(6).jpg",
                "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(5).jpg",
                "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(4).jpg",
                "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(3).jpg",
                "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(2).jpg"
            ]
            content_group_id = os.getenv('OTRA_HUBSPOT_BLOG_ID')
            blog_author_id = os.getenv('OTRA_HUBSPOT_AUTHOR_ID')

        image_url = images[index % len(images)]
        
        blog_post = {
            "name": title,
            "htmlTitle": title,
            "contentGroupId": content_group_id,
            "content": " ",
            "state": "DRAFT",
            "language": "es-cl",
            "blogAuthorId": blog_author_id,
            "slug": f"blog/{title}",
            "metaDescription": title,
            "postBody": f"""
            <img src="{image_url}" 
                alt="{title}" style="width:50%; max-width:800px; margin: 20px auto; display:block;">
            {content.strip()}
            """,
            "postSummary": f"<p>{title}</p>",
            "rssBody": content.strip(),
            "rssSummary": f"<p>{title}</p>",
            "featuredImage": image_url,
            "featuredImageAltText": title,
            "currentlyPublished": False,
            "publicAccessRulesEnabled": False,
            "publishImmediately": False,
            "publishDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        try:
            api_response = client.cms.blogs.blog_posts.blog_post_api.create(blog_post=blog_post)
            print(f"\n✅ Post {index} creado exitosamente en {'segundo' if is_second_execution else 'primer'} blog: {title}")
            return api_response
        except ApiException as e:
            print(f"Exception when calling blog_posts_api->create for post {index}: %s\n" % e)
            raise
        except Exception as e:
            print(f"\n❌ Error al crear el post {index}: {str(e)}")
            raise

    def _run(self, markdown_path: str, is_second_blog: bool = False) -> str:
        """Execute the tool with the given markdown path."""
        try:
            # Verificar si el input es un string JSON
            if isinstance(markdown_path, str) and markdown_path.startswith('['):
                import json
                try:
                    # Intentar parsear el JSON
                    posts = json.loads(markdown_path)
                    results = []
                    
                    # Procesar cada post
                    for post in posts:
                        if isinstance(post, dict):
                            path = post.get('markdown_path')
                            is_second = post.get('is_second_blog', False)
                            if path:
                                with open(path, 'r', encoding='utf-8') as file:
                                    content = file.read()
                                
                                # Crear cliente HubSpot según el blog
                                client = hubspot.Client.create(
                                    access_token=os.getenv('OTRA_HUBSPOT_API_KEY' if is_second else 'HUBSPOT_API_KEY')
                                )
                                
                                # Crear el post
                                response = self.create_blog_post(client, content, 1, is_second)
                                results.append(f"Post created successfully in {'second' if is_second else 'first'} blog")
                    
                    return " | ".join(results)
                except json.JSONDecodeError:
                    pass  # Si no es JSON válido, continuar con el proceso normal
            
            # Proceso normal para un solo post
            with open(markdown_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Crear cliente HubSpot según el blog
            if not is_second_blog:
                client = hubspot.Client.create(access_token=os.getenv('HUBSPOT_API_KEY'))
            else:
                client = hubspot.Client.create(access_token=os.getenv('OTRA_HUBSPOT_API_KEY'))
            
            # Crear el post
            response = self.create_blog_post(client, content, 1, is_second_blog)
            
            return f"Post created successfully in {'second' if is_second_blog else 'first'} blog"
            
        except Exception as e:
            return f"Error creating post: {str(e)}"
