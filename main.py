import os
import argparse
from dotenv import load_dotenv
from web_extractor import analyze_website_for_business_axes
from prompt_generator import generate_image_prompts
from generator_image import generate_multiple_images

def main():
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configurer l'analyseur d'arguments
    parser = argparse.ArgumentParser(description="Générateur d'images basé sur l'analyse d'un site web client")
    parser.add_argument("--url", type=str, help="URL du site web client à analyser")
    parser.add_argument("--output", type=str, default="images", help="Dossier de sortie pour les images générées")
    
    args = parser.parse_args()
    
    # Si aucune URL n'est fournie en argument, demander à l'utilisateur
    if not args.url:
        args.url = input("Entrez l'URL du site web client à analyser: ")
    
    print(f"\n1. ANALYSE DU SITE WEB: {args.url}")
    print("---------------------------------------------------")
    print("Extraction du contenu et conversion en Markdown...")
    # Analyser le site web pour identifier les axes d'activité
    business_axes = analyze_website_for_business_axes(args.url)
    
    print("\n2. AXES D'ACTIVITÉ IDENTIFIÉS:")
    print("---------------------------------------------------")
    for i, axis in enumerate(business_axes, 1):
        print(f"{i}. {axis}")
    
    print("\n3. GÉNÉRATION DES PROMPTS")
    print("---------------------------------------------------")
    # Générer des prompts pour les images basés sur les axes d'activité
    image_prompts = generate_image_prompts(business_axes)
    
    # Afficher les prompts générés
    for i, prompt in enumerate(image_prompts, 1):
        print(f"\nPrompt {i} (pour l'axe '{business_axes[i-1]}'):")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
    
    # Demander confirmation à l'utilisateur
    confirmation = input("\nVoulez-vous générer les images avec ces prompts? (O/n): ")
    if confirmation.lower() in ["", "o", "oui", "y", "yes"]:
        print("\n4. GÉNÉRATION DES IMAGES")
        print("---------------------------------------------------")
        # Générer les images
        image_files = generate_multiple_images(image_prompts, args.output)
        
        print("\n5. RÉSUMÉ")
        print("---------------------------------------------------")
        if image_files:
            print(f"{len(image_files)} images ont été générées dans le dossier '{args.output}':")
            for i, file in enumerate(image_files, 1):
                print(f"{i}. {file} - Basée sur l'axe: '{business_axes[i-1]}'")
        else:
            print("Aucune image n'a été générée. Vérifiez les erreurs ci-dessus.")
    else:
        print("Génération d'images annulée.")

if __name__ == "__main__":
    main()