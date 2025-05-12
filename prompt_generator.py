from config_azure_openai import init_azure_openai, get_deployment_info

def generate_image_prompts(business_axes):
    """
    Génère des prompts détaillés pour la création de publicité à partir des axes d'activité
    """
    if not business_axes or len(business_axes) == 0:
        return ["Prompt par défaut: Une publicité d'entreprise professionnelle"]
    
    # Initialiser le client Azure OpenAI
    client = init_azure_openai()
    deployment_info = get_deployment_info()
    
    image_prompts = []
    
    for axis in business_axes:
        try:
            prompt = f"""
            Tu es un expert en génération de publicité pour le marketing. Ton objectif est de créer un prompt détaillé pour générer une publicité qui représente parfaitement l'axe d'activité suivant: "{axis}".
            
            Le prompt doit:
            1. Être très détaillé et précis pour un générateur de publicité AI
            2. Inclure des éléments visuels spécifiques qui représentent cet axe d'activité
            3. Spécifier le style (photo réaliste, style photographique, etc.)
            4. Préciser l'ambiance et les couleurs dominantes qui correspondent à cet axe
            5. Être optimisé pour une utilisation professionnelle et marketing
            6. Étre en anglais
            7. Le texte dans la publicité doit etre obligatoirement present ,Centré et etre en FRANCAIS
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
            image_prompts.append(f"Prompt de secours pour {axis}: publicité professionnelle représentant {axis}")
    
    return image_prompts