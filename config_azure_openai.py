from dotenv import load_dotenv
import os
from openai import AzureOpenAI

def init_azure_openai():
    """
    Initialise et configure le client Azure OpenAI
    """
    load_dotenv()
    
    # Configuration pour Azure OpenAI
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Vérification des variables d'environnement
    if not api_key or not azure_endpoint:
        raise ValueError("Les variables d'environnement AZURE_OPENAI_API_KEY et AZURE_OPENAI_ENDPOINT doivent être définies")
    
    # Création du client Azure OpenAI
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=azure_endpoint
    )
    
    return client

def get_deployment_info():
    """
    Retourne les noms des déploiements configurés pour les modèles GPT
    """
    return {
        "gpt_deployment": os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT", "gpt4o"),
    }