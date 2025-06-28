"""
OpenAI client management and embedding generation.
"""

import os
from openai import OpenAI
from config import config


class OpenAIService:
    """Service for managing OpenAI client and operations."""

    def __init__(self):
        self._client = None

    def get_client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self._client is None:
            if config.openai_api_key is not None:
                # Only set the environment variable if it was successfully retrieved
                os.environ["OPENAI_API_KEY"] = config.openai_api_key
            else:
                print("Warning: OPENAI_API_KEY environment variable is not set.")

            self._client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        return self._client

    def get_embeddings(self, query: str) -> list:
        """Generate embeddings for a query."""
        client = self.get_client()
        embeddings = client.embeddings.create(
            model="text-embedding-ada-002",
            input=[query],
        )
        return embeddings.data[0].embedding

    def generate_completion(self, messages: list, model: str = "gpt-4o") -> str:
        """Generate a chat completion."""
        client = self.get_client()
        chat_completion = client.chat.completions.create(messages=messages, model=model)
        return chat_completion.choices[0].message.content


# Global service instance
openai_service = OpenAIService()
