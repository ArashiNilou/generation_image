from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import base64
from datetime import datetime
import uuid
from openai import OpenAI
from dotenv import load_dotenv

def init_openai_client():
    """
    Initialise et retourne le client OpenAI
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("La variable d'environnement OPENAI_API_KEY doit être définie")
    
    return OpenAI(api_key=api_key)

def generate_image_with_assets(prompt, logo_path=None, colors=None, output_folder="images"):
    """
    Génère une publicité à partir d'un prompt en utilisant OpenAI gpt-image-1
    puis intègre le logo de l'entreprise
    """
    print(f"Génération de la publicité pour le prompt: {prompt[:50]}...")
    
    # Initialiser le client OpenAI
    client = init_openai_client()
    
    try:
        # Générer publicité de base
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
        base_filename = f"{output_folder}/image_{timestamp}_{unique_id}"
        raw_image_filename = f"{base_filename}_raw.png"
        final_filename = f"{base_filename}.png"
        
        # Sauvegarder l'image brute
        image_data = base64.b64decode(img_response.data[0].b64_json)
        with open(raw_image_filename, "wb") as f:
            f.write(image_data)
        
        # Si un logo est disponible, l'intégrer à l'image
        if logo_path and os.path.exists(logo_path):
            try:
                # Ouvrir l'image générée et le logo
                base_image = Image.open(BytesIO(image_data))
                logo = Image.open(logo_path)
                
                # Redimensionner le logo pour qu'il ne dépasse pas 20% de la largeur de l'image
                max_logo_width = int(base_image.width * 0.2)
                logo_ratio = logo.width / logo.height
                new_logo_width = min(max_logo_width, logo.width)
                new_logo_height = int(new_logo_width / logo_ratio)
                logo = logo.resize((new_logo_width, new_logo_height), Image.LANCZOS)
                
                # Calculer la position du logo (haut gauche avec une marge)
                position = (20, 20)
                
                # Créer un masque pour le logo si nécessaire (si le logo a un canal alpha)
                if logo.mode == 'RGBA':
                    logo_mask = logo.split()[3]  # Canal alpha
                else:
                    logo_mask = None
                
                # Coller le logo sur l'image de base
                base_image.paste(logo, position, logo_mask)
                
                # Sauvegarder l'image finale
                base_image.save(final_filename)
                
                print(f"Image avec logo sauvegardée: {final_filename}")
                return final_filename
            except Exception as e:
                print(f"Erreur lors de l'ajout du logo: {e}")
                print(f"Utilisation de l'image brute: {raw_image_filename}")
                return raw_image_filename
        else:
            # Si pas de logo, utiliser l'image brute
            os.rename(raw_image_filename, final_filename)
            print(f"Image sauvegardée: {final_filename}")
            return final_filename
    
    except Exception as e:
        print(f"Erreur lors de la génération de la publicité: {e}")
        return None

def generate_multiple_images_with_assets(prompts, visual_identity, output_folder="images"):
    """
    Génère plusieurs publicités à partir d'une liste de prompts
    en intégrant les éléments d'identité visuelle
    """
    generated_files = []
    
    logo_path = visual_identity["logo"]["path"] if visual_identity["logo"] else None
    colors = visual_identity["colors"] if visual_identity["colors"] else None
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nGénération d'image {i}/{len(prompts)}")
        file_path = generate_image_with_assets(prompt, logo_path, colors, output_folder)
        if file_path:
            generated_files.append(file_path)
    
    return generated_files