# Create utils/openai_client.py
from openai import OpenAI
from dotenv import load_dotenv

from config.settings import settings

load_dotenv()

# Singleton pattern for OpenAI client
class OpenAIClient:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return cls._instance
    
    @property
    def client(self):
        return self._client

# Usage in other files
# from config import settings
# from utils.openai_client import OpenAIClient
# client = OpenAIClient().client