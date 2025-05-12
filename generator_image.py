from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import time
from datetime import datetime
import uuid

def init_openai_client():
    """
    Initialise et retourne le client OpenAI
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("La variable d'environnement OPENAI_API_KEY doit être définie")
    
    return OpenAI(api_key=api_key)

def generate_image(prompt, output_folder="images"):
    """
    Génère une publicité à partir d'un prompt en utilisant OpenAI gpt-image-1
    """
    print(f"Génération de la publicité pour le prompt: {prompt[:50]}...")
    
    # Initialiser le client OpenAI
    client = init_openai_client()
    
    try:
        # Générer publicité
        img_response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            background="auto",
            n=1,
            quality="high",
            size="1024x1024",
            output_format="png",
            moderation="auto",
        )
        
        # Créer le dossier de sortie s'il n'existe pas
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Générer un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{output_folder}/image_{timestamp}_{unique_id}.png"
        
        # Sauvegarder l'image
        image_data = base64.b64decode(img_response.data[0].b64_json)
        with open(filename, "wb") as f:
            f.write(image_data)
        
        print(f"Image sauvegardée: {filename}")
        return filename
    
    except Exception as e:
        print(f"Erreur lors de la génération de la publicité: {e}")
        return None

def generate_multiple_images(prompts, output_folder="images"):
    """
    Génère plusieurs publicités à partir d'une liste de prompts
    """
    generated_files = []
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nGénération d'image {i}/{len(prompts)}")
        file_path = generate_image(prompt, output_folder)
        if file_path:
            generated_files.append(file_path)
    
    return generated_files