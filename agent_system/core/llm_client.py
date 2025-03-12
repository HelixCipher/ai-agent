import requests
from typing import Dict, Any
import json
import os
from groq import Groq


class LLMClient:
    """Handles communication with the Groq LLM API."""
    
    def __init__(self, api_key: str = None, model: str = "llama3-8b-8192"):
        # Use provided API key or load it from environment variables
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing. Ensure it is set in the environment or passed as an argument.")
        
        self.model = model
        # Initialize the Groq client
        self.client = Groq(api_key=self.api_key)
    
    def query(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> str:
        """Send a query to the LLM and return the response."""
        try:
            # Use Groq's `chat.completions.create` method for chat completions
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            # Return the generated content
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"LLM query failed: {str(e)}")
