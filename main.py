import os
import argparse
from dotenv import load_dotenv
from web_extractor import analyze_website_for_business_axes
from business_analyzer import generate_business_description, extract_website_visual_identity
from enhanced_image_generator import generate_multiple_images_with_assets
from business_analyzer import generate_ad_prompts_with_visual_identity

def main():
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configurer l'analyseur d'arguments
    parser = argparse.ArgumentParser(description="Générateur d'images publicitaires avancé basé sur l'analyse d'un site web")
    parser.add_argument("--url", type=str, help="URL du site web client à analyser")
    parser.add_argument("--output", type=str, default="images", help="Dossier de sortie pour les images générées")
    
    args = parser.parse_args()
    
    # Si aucune URL n'est fournie en argument, demander à l'utilisateur
    if not args.url:
        args.url = input("Entrez l'URL du site web client à analyser: ")
    
    print(f"\n1. ANALYSE DU SITE WEB: {args.url}")
    print("---------------------------------------------------")
    print("Extraction du contenu et analyse...")
    
    # Analyser le site web pour identifier les axes d'activité
    business_axes = analyze_website_for_business_axes(args.url)
    
    # Générer une description concise de l'entreprise
    print("\nGénération de la description de l'entreprise...")
    business_description = generate_business_description(args.url)
    
    # Extraire l'identité visuelle (logo, images, couleurs)
    print("\nExtraction de l'identité visuelle (logo, images, couleurs)...")
    visual_identity = extract_website_visual_identity(args.url)
    
    print("\n2. INFORMATIONS EXTRAITES:")
    print("---------------------------------------------------")
    print(f"Description de l'entreprise: {business_description}")
    print(f"\nLogo extrait: {'Oui - ' + visual_identity['logo']['path'] if visual_identity['logo']['path'] else 'Non'}")
    print(f"Palette de couleurs: {', '.join(visual_identity['colors'][:3]) if visual_identity['colors'] else 'Non disponible'}")
    print(f"Images principales: {len(visual_identity['main_images']) if visual_identity['main_images'] else 0} images extraites")
    
    print("\n3. AXES D'ACTIVITÉ IDENTIFIÉS:")
    print("---------------------------------------------------")
    for i, axis in enumerate(business_axes, 1):
        print(f"{i}. {axis}")
    
    print("\n4. GÉNÉRATION DES PROMPTS AVEC IDENTITÉ VISUELLE")
    print("---------------------------------------------------")
    # Générer des prompts pour les images en intégrant l'identité visuelle
    image_prompts = generate_ad_prompts_with_visual_identity(business_axes, visual_identity)
    
    # Afficher les prompts générés
    for i, prompt in enumerate(image_prompts, 1):
        print(f"\nPrompt {i} (pour l'axe '{business_axes[i-1]}'):")
        print("-" * 50)
        print(prompt)
        print("-" * 50)
    
    # Demander confirmation à l'utilisateur
    confirmation = input("\nVoulez-vous générer les images avec ces prompts? (O/n): ")
    if confirmation.lower() in ["", "o", "oui", "y", "yes"]:
        print("\n5. GÉNÉRATION DES IMAGES AVEC LOGO")
        print("---------------------------------------------------")
        # Générer les images en intégrant le logo et les couleurs
        image_files = generate_multiple_images_with_assets(image_prompts, visual_identity, args.output)
        
        print("\n6. RÉSUMÉ")
        print("---------------------------------------------------")
        if image_files:
            print(f"{len(image_files)} images ont été générées dans le dossier '{args.output}':")
            for i, file in enumerate(image_files, 1):
                print(f"{i}. {file} - Basée sur l'axe: '{business_axes[i-1]}'")
        else:
            print("Aucune image n'a été générée. Vérifiez les erreurs ci-dessus.")
    else:
        print("Génération d'images annulée.")
    
    # Afficher les informations pour l'interface utilisateur
    print("\n7. INFORMATIONS POUR L'INTERFACE UTILISATEUR")
    print("---------------------------------------------------")
    print(f"Description de l'entreprise pour affichage: {business_description}")
    if visual_identity['logo']['path']:
        print(f"Chemin du logo pour affichage: {visual_identity['logo']['path']}")

if __name__ == "__main__":
    main()