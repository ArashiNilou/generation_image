import requests
from bs4 import BeautifulSoup
import os
import re
import urllib.parse
from logo_extractor import extract_logo, download_logo, extract_main_images, extract_color_palette

def generate_business_description(url):
    """
    Génère une description concise de l'entreprise basée sur le contenu du site web
    """
    # Cette fonction est probablement déjà implémentée dans votre code
    # Je laisse donc votre implémentation existante
    try:
        # Exemple simplifié - à remplacer par votre code
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraire la description des balises meta
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc.get('content')
            
        # Si pas de meta description, chercher dans d'autres éléments
        # [Votre logique ici]
        
        return "Description non disponible"
    except Exception as e:
        print(f"Erreur lors de la génération de la description: {e}")
        return "Description non disponible"
    
def extract_website_visual_identity(url):
    """
    Extrait l'identité visuelle d'un site web (logo, images principales, palette de couleurs)
    """
    try:
        # Créer les dossiers de sortie s'ils n'existent pas
        if not os.path.exists("logos"):
            os.makedirs("logos")
        
        # Extraire le logo
        logo_info = extract_logo(url)
        
        # Structure pour stocker l'identité visuelle
        visual_identity = {
            'logo': {
                'info': logo_info,
                'path': None
            },
            'main_images': [],
            'colors': []
        }
        
        # Télécharger le logo si trouvé
        if logo_info:
            logo_path = download_logo(logo_info, "logos")
            if logo_path:
                visual_identity['logo']['path'] = logo_path
        
        # Extraire les images principales
        main_images = extract_main_images(url)
        visual_identity['main_images'] = main_images
        
        # Extraire la palette de couleurs
        colors = extract_color_palette(url)
        visual_identity['colors'] = colors
        
        return visual_identity
    
    except Exception as e:
        print(f"Erreur lors de l'extraction de l'identité visuelle: {e}")
        # Retourner une structure par défaut en cas d'erreur
        return {
            'logo': {
                'info': None,
                'path': None
            },
            'main_images': [],
            'colors': ["#1a73e8", "#ffffff", "#333333"]  # Couleurs par défaut
        }

def generate_ad_prompts_with_visual_identity(business_axes, visual_identity):
    """
    Génère des prompts pour les images publicitaires en intégrant l'identité visuelle
    """
    # Cette fonction est probablement déjà implémentée dans votre code
    # Je laisse donc votre implémentation existante
    
    # Exemple simplifié - à remplacer par votre code
    prompts = []
    for axis in business_axes:
        # Génération d'un prompt qui intègre l'identité visuelle
        colors_info = ""
        if visual_identity['colors']:
            colors_info = f" en utilisant les couleurs {', '.join(visual_identity['colors'][:3])}"
        
        prompt = f"Création d'une image publicitaire professionnelle illustrant '{axis}'{colors_info}. L'image doit être claire, élégante et adaptée à une utilisation sur les réseaux sociaux."
        
        prompts.append(prompt)
    
    return prompts