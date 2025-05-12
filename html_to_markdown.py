from dotenv import load_dotenv
import os
import requests
from typing import Optional

def init_html_to_markdown_api():
    """
    Initialise la configuration pour l'API de conversion HTML vers Markdown
    """
    load_dotenv()
    
    # Récupérer le token API depuis les variables d'environnement
    api_token = os.getenv("HTML_TO_MARKDOWN_API_TOKEN")
    
    if not api_token:
        raise ValueError("La variable d'environnement HTML_TO_MARKDOWN_API_TOKEN doit être définie")
    
    return api_token

def convert_html_to_markdown(url: str) -> Optional[str]:
    """
    Convertit le contenu d'une URL en Markdown en utilisant l'API

    Args:
        url (str): L'URL à convertir

    Returns:
        Optional[str]: Le contenu converti en Markdown ou None en cas d'erreur
    """
    api_token = init_html_to_markdown_api()

    try:
        api_url = "https://markdown.innovation-additi.fr/api/html-to-markdown"

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "url": url
        }

        print("Envoi de la requête à l'API avec l'URL:", url)
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()

        if "content" in result:
            print("Conversion en Markdown réussie")
            return result["content"]
        else:
            print(f"Erreur: La réponse de l'API ne contient pas de champ 'content': {result}")
            return None

    except Exception as e:
        print(f"Erreur lors de la conversion de l'URL: {e}")
        return None

