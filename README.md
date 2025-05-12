# Générateur d'Images basé sur l'Analyse de Site Web

Ce projet analyse automatiquement un site web d'entreprise, identifie ses 4 principaux axes d'activité, génère des prompts pertinents, puis crée des images correspondantes à l'aide d'OpenAI gpt-image-1.


. Le système analyse le site web pour identifier les 4 axes principaux d'activité
. Pour chaque axe, un prompt détaillé est généré pour créer une image pertinente
. Les prompts sont présentés à l'utilisateur pour validation
. Après confirmation, les images sont générées et sauvegardées localement


Les images générées seront sauvegardées dans le dossier `images` par défaut.

## Personnalisation

- Créer et configurer votre fichier .env avec les info suivantes:
- OPENAI_API_KEY
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT
- AZURE_OPENAI_API_VERSION
- AZURE_OPENAI_GPT_DEPLOYMENT
- API html to markdown créé paar Melaine:
- HTML_TO_MARKDOWN_API_TOKEN

Vous pouvez modifier les scripts pour adapter le système à vos besoins spécifiques:

- Ajuster les prompts système dans `web_extractor.py` et `prompt_generator.py`
- Modifier les paramètres de génération d'images dans `generator_image.py`
- Changer le format ou le style des images générées


 Pour les sites web complexes, essayez d'ajuster les paramètres d'extraction dans `web_extractor.py`
