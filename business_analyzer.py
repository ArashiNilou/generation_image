from dotenv import load_dotenv
import os
from html_to_markdown import convert_html_to_markdown
from config_azure_openai import init_azure_openai, get_deployment_info
from logo_extractor import extract_logo, download_logo, extract_main_images, extract_color_palette

def generate_business_description(url):
    """
    Génère une description concise des activités de l'entreprise à partir du contenu Markdown du site web
    """
    # Convertir le contenu HTML en Markdown
    markdown_content = convert_html_to_markdown(url)
    
    if not markdown_content:
        print("Erreur: Impossible de récupérer le contenu Markdown du site")
        return "Description non disponible"
    
    # Initialiser le client Azure OpenAI
    client = init_azure_openai()
    deployment_info = get_deployment_info()
    
    # Préparer le prompt pour la génération de la description
    prompt = f"""
    Tu es un expert en analyse d'entreprise. Analyse le contenu suivant extrait d'un site web d'entreprise (converti en format Markdown) et génère une description concise et précise des activités de l'entreprise.

    La description doit:
    1. Être très claire et directe (maximum 3 phrases)
    2. Expliquer précisément le secteur d'activité de l'entreprise
    3. Mentionner les principaux produits ou services offerts
    4. Mettre en évidence ce qui distingue cette entreprise de ses concurrents
    5. Être adaptée pour un affichage dans une interface utilisateur

    Contenu du site:
    {markdown_content[:8000]}  # Limiter à 8000 caractères pour éviter les dépassements de tokens
    
    Format de réponse: Un paragraphe court et précis, sans introduction ni conclusion.
    """
    
    try:
        response = client.chat.completions.create(
            model=deployment_info["gpt_deployment"],
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse d'entreprise qui crée des descriptions concises et précises d'entreprises à partir du contenu de leur site web."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        # Extraire la description générée
        description = response.choices[0].message.content.strip()
        return description
    except Exception as e:
        print(f"Erreur lors de la génération de la description: {e}")
        return "Description non disponible"

def extract_website_visual_identity(url):
    """
    Extrait l'identité visuelle d'un site web (logo, images principales, couleurs)
    """
    # Extraire le logo
    logo_info = extract_logo(url)
    if logo_info:
        logo_path = download_logo(logo_info)
    else:
        logo_path = None
    
    # Extraire les images principales
    main_images = extract_main_images(url)
    
    # Extraire la palette de couleurs
    colors = extract_color_palette(url)
    
    return {
        "logo": {
            "info": logo_info,
            "path": logo_path
        },
        "main_images": main_images,
        "colors": colors
    }

def generate_ad_prompts_with_visual_identity(business_axes, visual_identity):
    """
    Génère des prompts d'images publicitaires en intégrant l'identité visuelle extraite
    """
    # Initialiser le client Azure OpenAI
    client = init_azure_openai()
    deployment_info = get_deployment_info()
    
    image_prompts = []
    
    # Préparer les informations sur l'identité visuelle
    logo_info = "Logo d'entreprise présent en haut à gauche" if visual_identity["logo"]["path"] else "Logo d'entreprise non disponible"
    colors_info = ", ".join(visual_identity["colors"][:3]) if visual_identity["colors"] else "Palette de couleurs non disponible"
    images_info = f"{len(visual_identity['main_images'])} images principales extraites" if visual_identity["main_images"] else "Aucune image principale extraite"
    
    for axis in business_axes:
        try:
            prompt = f"""
            Tu es un expert en génération de publicité pour le marketing. Ton objectif est de créer un prompt détaillé pour générer une publicité qui représente parfaitement l'axe d'activité suivant: "{axis}".
            
            Utilise les éléments d'identité visuelle suivants du site web:
            - {logo_info}
            - Couleurs principales: {colors_info}
            - {images_info}
            
            Le prompt doit:
            1. Être très détaillé et précis pour un générateur de publicité AI
            2. Inclure des éléments visuels spécifiques qui représentent cet axe d'activité
            3. Spécifier le style (photo réaliste, style photographique, etc.)
            4. Préciser l'ambiance et utiliser les couleurs mentionnées ci-dessus
            5. Être optimisé pour une utilisation professionnelle et marketing
            6. Être en anglais
            7. Le texte dans la publicité doit être obligatoirement présent, centré et être en FRANÇAIS
            8. Intégrer le logo de l'entreprise en haut à gauche de la publicité
            
            Format de réponse: Un seul paragraphe de prompt optimisé, sans introduction ni conclusion.
            """
            
            response = client.chat.completions.create(
                model=deployment_info["gpt_deployment"],
                messages=[
                    {"role": "system", "content": "Tu es un expert en création de prompts pour la génération de publicité AI professionnelles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Extraire et nettoyer le prompt généré
            image_prompt = response.choices[0].message.content.strip()
            image_prompts.append(image_prompt)
            
        except Exception as e:
            print(f"Erreur lors de la génération du prompt pour l'axe '{axis}': {e}")
            image_prompts.append(f"Prompt de secours pour {axis}: publicité professionnelle représentant {axis} avec le logo de l'entreprise en haut à gauche et utilisant les couleurs {colors_info}")
    
    return image_prompts