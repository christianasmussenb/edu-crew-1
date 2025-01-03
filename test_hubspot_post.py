import os
import hubspot
from hubspot.cms.blogs.blog_posts import BlogPost, ApiException
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

def md_to_html(md_content):
    """Convierte el contenido markdown a HTML manteniendo el formato"""
    html = md_content
    
    # Headers primero
    html = html.replace('  ', ' ')  # Eliminar espacios dobles
    html = html.replace('# ', '<h2>').replace('\n# ', '\n<h2>')  # Títulos principales
    html = html.replace('## ', '<h4>').replace('\n## ', '\n<h4>')  # Subtítulos
    
    # Cerrar headers
    html = html.replace('\n', '</h2>', 1) if html.startswith('<h2>') else html
    html = html.replace('\n', '</h4>') if '<h4>' in html else html
    
    # Ahora sí limpiar cualquier # residual
    html = html.replace('#', '')
    
    # Párrafos sin líneas extra
    paragraphs = [p.strip() for p in html.split('\n\n') if p.strip()]
    html = '\n'.join(f'<p>{p}</p>' if not p.startswith('<h') else p 
                     for p in paragraphs)
    
    return html

def create_blog_post(client, content, index, is_second_execution=False):
    """Crea un post de blog individual"""
    title = content.split('\n')[0].replace('# ', '').replace('##', '').strip()
    title = title[:60]
    
    # Seleccionar configuración según la ejecución
    if not is_second_execution:
        images = [
            "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/1_edICTq8-DfLxpOJE38hEmA.jpeg",
            "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/pexels-photo-3313333.jpg",
            "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/AdobeStock_409843373-1.jpeg",
            "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/pexels-photo-3313333.jpg",
            "https://45461238.fs1.hubspotusercontent-na1.net/hubfs/45461238/1_edICTq8-DfLxpOJE38hEmA.jpeg"
        ]
        content_group_id = "160750783103"
        blog_author_id = "160742183605"
    else:
        images = [
            "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(6).jpg",
            "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(5).jpg",
            "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(4).jpg",
            "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(3).jpg",
            "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(2).jpg",
            "https://www.casmuss.com/hubfs/Copy%20of%20HTC%20-Casos%20de%20Exito%205x5%20(1).jpg"
        ]
        content_group_id = "49891678929"
        blog_author_id = "51700133830"

    image_url = images[index % len(images)]
    
    blog_post = {
        "name": title,
        "htmlTitle": title,
        "contentGroupId": content_group_id,
        "content": " ",
        "state": "DRAFT",
        "language": "es-cl",
        "blogAuthorId": blog_author_id,
        "slug": f"blog/healthcare-ai-part-{index}",
        "metaDescription": "Avances en medicina usando IA: " + title,
        "postBody": f"""
        <img src="{image_url}" 
             alt="IA en medicina" style="width:100%; max-width:800px; margin: 20px auto; display:block;">
        {md_to_html(content)}
        """,
        "postSummary": f"<p>{title}</p>",
        "rssBody": md_to_html(content),
        "rssSummary": f"<p>{title}</p>",
        "featuredImage": image_url,
        "featuredImageAltText": "IA en medicina",
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
    except Exception as e:
        print(f"\n❌ Error al crear el post {index}: {str(e)}")

def test_hubspot_post_sdk():
    HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY')
    OTRA_HUBSPOT_API_KEY = os.getenv('OTRA_HUBSPOT_API_KEY')
    
    # Leer el archivo markdown
    md_file_path = "edu_flow2/output/Healthcare,_latest_advancements_in_medicine_using_AI_begginer.md"
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Dividir el contenido en secciones
    sections = content.split('------')
    
    # Primera ejecución
    try:
        client = hubspot.Client.create(access_token=HUBSPOT_API_KEY)
        print("\n🚀 Iniciando primera ejecución...")
        for i, section in enumerate(sections, 1):
            if section.strip():
                create_blog_post(client, section.strip(), i, False)
    except Exception as e:
        print(f"Error en primera ejecución: {str(e)}")
    
    # Segunda ejecución
    try:
        client2 = hubspot.Client.create(access_token=OTRA_HUBSPOT_API_KEY)
        print("\n🚀 Iniciando segunda ejecución...")
        for i, section in enumerate(sections, 1):
            if section.strip():
                create_blog_post(client2, section.strip(), i, True)
    except Exception as e:
        print(f"Error en segunda ejecución: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando creación de múltiples posts en HubSpot...")
    test_hubspot_post_sdk()