# agent.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.openai_client import OpenAIClient

load_dotenv()  # Load environment variables from .env

client = OpenAIClient().client

def simple_agent(prompt: str) -> str:
    """Send prompt to GPT-4 and return the response."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful AI agent."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
