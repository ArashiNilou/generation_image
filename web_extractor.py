import requests
from bs4 import BeautifulSoup
import trafilatura
from config_azure_openai import init_azure_openai, get_deployment_info
from html_to_markdown import convert_html_to_markdown

def extract_website_content(url):
    """
    Extrait le contenu textuel d'un site web en utilisant l'API de conversion HTML vers Markdown
    Si l'API échoue, utilise des méthodes alternatives (trafilatura ou extraction directe)
    """
    # Essayer d'abord avec l'API HTML vers Markdown
    print("Tentative d'extraction avec l'API HTML vers Markdown...")
    markdown_content = convert_html_to_markdown(url)
    
    if markdown_content:
        print("Extraction réussie via l'API HTML vers Markdown")
        return markdown_content
    
    # Si l'API échoue, essayer avec trafilatura
    print("L'API a échoué, tentative avec trafilatura...")
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            if text:
                print("Extraction réussie via trafilatura")
                return text.strip()
            else:
                return extract_fallback(url)
        else:
            return extract_fallback(url)
    except Exception as e:
        print(f"Erreur lors de l'extraction avec trafilatura: {e}")
        return extract_fallback(url)

def extract_fallback(url):
    """
    Méthode de secours pour extraire le contenu d'un site web si les autres méthodes échouent
    """
    print("Utilisation de la méthode de secours pour l'extraction...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Supprimer les éléments non pertinents
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()
            
        # Extraire le texte
        text = soup.get_text(separator='\n')
        
        # Nettoyer le texte
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        print("Extraction réussie via la méthode de secours")
        return cleaned_text
    except Exception as e:
        print(f"Erreur lors de l'extraction fallback: {e}")
        return f"Échec de l'extraction du contenu de {url}: {str(e)}"

def analyze_website_for_business_axes(url):
    """
    Analyse un site web pour identifier les 4 axes principaux d'activité
    en utilisant Azure OpenAI
    """
    # Extraire le contenu du site
    content = extract_website_content(url)
    
    if not content or len(content) < 100:
        return ["Échec de l'extraction du contenu suffisant"]
    
    # Initialiser le client Azure OpenAI
    client = init_azure_openai()
    deployment_info = get_deployment_info()
    
    # Préparer la requête pour l'analyse des axes d'activité
    prompt = f"""
    Tu es un expert en analyse d'entreprise. Analyse le contenu suivant extrait d'un site web d'entreprise (converti en format Markdown) et identifie précisément les 4 axes principaux d'activité.
    Pour chaque axe, donne un titre concis mais précis qui reflète fidèlement cette activité.
    Format de réponse - seulement les 4 axes, un par ligne, sans numérotation ni ponctuation:
    
    {content[:10000]}  # Limiter à 10 000 caractères pour éviter les dépassements de tokens
    """
    
    try:
        response = client.chat.completions.create(
            model=deployment_info["gpt_deployment"],
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse d'entreprise qui identifie les axes d'activité principaux d'une entreprise à partir du contenu Markdown de son site web."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        # Extraire et nettoyer les axes d'activité
        axes_text = response.choices[0].message.content.strip()
        axes = [line.strip() for line in axes_text.split('\n') if line.strip()]
        
        # Limiter à 4 axes
        return axes[:4]
    except Exception as e:
        print(f"Erreur lors de l'analyse des axes d'activité: {e}")
        return [f"Erreur d'analyse: {str(e)}"]
