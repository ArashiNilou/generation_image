# IA Générateur de Publicités Automatisé

Un outil d'analyse de sites web et de génération automatique de publicités personnalisées intégrant l'identité visuelle de l'entreprise.

## Description du projet

Ce projet est un système automatisé qui:
1. Analyse un site web d'entreprise pour comprendre ses activités
2. Extrait son identité visuelle (logo, couleurs, images)
3. Identifie les principaux axes d'activité
4. Génère une description concise de l'entreprise
5. Crée des publicités ciblées personnalisées avec le logo intégré

Le système utilise les technologies d'IA avancées (OpenAI GPT-4o et DALL-E) pour analyser le contenu et générer des publicités professionnelles adaptées à chaque aspect de l'activité de l'entreprise.

## Fonctionnalités

- **Analyse automatique de sites web**: Extraction et analyse du contenu textuel et visuel
- **Extraction intelligente de logo**: Détection et récupération automatique du logo de l'entreprise
- **Analyse de l'identité visuelle**: Détermination des couleurs principales du site
- **Identification des axes d'activité**: Détection des 4 principaux domaines d'activité
- **Génération de description d'entreprise**: Création d'un texte concis expliquant l'activité
- **Création de prompts optimisés**: Génération de directives précises pour la création d'images
- **Génération d'images publicitaires**: Production de visuels professionnels intégrant le logo

## Prérequis

- Python 3.8+
- Compte OpenAI avec clé API (ou compte Azure OpenAI)
- API HTML to Markdown (token d'accès requis)

## Installation

1. Clonez ce dépôt:
```bash
git clone https://github.com/votre-nom/ia-generateur-publicites.git
cd ia-generateur-publicites
```

2. Installez les dépendances:
```bash
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet avec les variables suivantes:
```
# OpenAI API (obligatoire)
OPENAI_API_KEY=votre_cle_api_openai

# HTML to Markdown API (obligatoire)
HTML_TO_MARKDOWN_API_TOKEN=votre_token_api_markdown

# Azure OpenAI (optionnel - si vous utilisez Azure au lieu d'OpenAI)
AZURE_OPENAI_API_KEY=votre_cle_api_azure
AZURE_OPENAI_ENDPOINT=votre_endpoint_azure
AZURE_OPENAI_API_VERSION=votre_version_api
AZURE_OPENAI_DEPLOYMENT_GPT=votre_nom_deployment
```

## Utilisation

### Exécution basique

```bash
python main_enhanced.py --url https://www.exemple.fr --output images
```

Options:
- `--url`: URL du site web à analyser (obligatoire)
- `--output`: Dossier de sortie pour les images générées (par défaut: "images")

### Processus d'exécution

1. **Analyse du site web**: Extraction et conversion du contenu en Markdown
2. **Identification des axes d'activité**: Détection des principales activités de l'entreprise
3. **Génération de la description**: Création d'un texte concis décrivant l'entreprise
4. **Extraction de l'identité visuelle**: Récupération du logo et des couleurs principales
5. **Génération des prompts**: Création de directives pour chaque axe d'activité
6. **Création des images publicitaires**: Génération d'images avec intégration du logo
7. **Affichage des résultats**: Présentation des images générées et du récapitulatif

## Structure des fichiers

```
.
├── main_enhanced.py        # Script principal d'exécution
├── business_analyzer.py    # Analyse des activités et génération de descriptions
├── logo_extractor.py       # Extraction de logos et d'identité visuelle
├── enhanced_image_generator.py  # Génération d'images avec intégration de logo
├── web_extractor.py        # Extraction du contenu des sites web
├── html_to_markdown.py     # Conversion HTML en Markdown
├── config_azure_openai.py  # Configuration pour Azure OpenAI
└── requirements.txt        # Dépendances du projet
```

## Exemples de sortie

### Description d'entreprise
```
ExempleEntreprise est une agence de marketing digital spécialisée dans l'optimisation SEO, le développement web et la gestion des réseaux sociaux pour les PME.
```

### Images générées
Le système génère des images publicitaires pour chaque axe d'activité identifié, avec le logo de l'entreprise intégré dans le coin supérieur gauche.

## Limitations

- L'analyse est limitée au contenu textuel et aux éléments visuels accessibles publiquement
- La qualité de l'extraction du logo dépend de la structure du site web
- Les sites web avec des protections anti-scraping peuvent ne pas fonctionner correctement
- L'extraction fonctionne mieux sur des sites avec une structure HTML standard

## Dépannage

### Problèmes courants

1. **Erreur d'API OpenAI**
   - Vérifiez que votre clé API est valide et dispose de crédits suffisants
   - Assurez-vous que la variable d'environnement OPENAI_API_KEY est correctement définie

2. **Échec de l'extraction du logo**
   - Essayez avec un autre site web pour vérifier si le problème est spécifique au site
   - Consultez les journaux pour identifier le point d'échec dans la détection

3. **Problèmes avec l'API HTML to Markdown**
   - Vérifiez la validité de votre token d'API
   - Assurez-vous que l'API est en ligne et accessible
