"""
Configuration settings for the application.
Supports multiple database providers (Astra DB and Azure Search).
"""

import os
from typing import Optional


class Config:
    """Application configuration class supporting multiple database providers."""

    def __init__(self):
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Database provider selection
        self.database_provider = os.getenv("DATABASE_PROVIDER", "astra").lower()

        # Astra DB configuration
        self.astra_token = os.getenv("ASTRADB_TOKEN")
        self.astra_endpoint = os.getenv("ASTRADB_ENDPOINT", "")
        self.astra_keyspace = os.getenv("ASTRADB_KEYSPACE", "default_keyspace")

        # Azure Search configuration
        self.azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.azure_search_key = os.getenv("AZURE_SEARCH_KEY")
        self.azure_search_api_version = os.getenv("AZURE_SEARCH_API_VERSION", "2023-11-01")

        # Legacy database property for backwards compatibility
        self._client = None
        self._db = None

    @property
    def database(self):
        """
        Get the database connection for backwards compatibility.
        This maintains compatibility with existing code while supporting the new architecture.
        """
        if self.database_provider == "astra":
            return self._get_astra_database()
        else:
            # For non-Astra providers, return None and let the new service handle it
            return None

    def _get_astra_database(self):
        """Get Astra DB connection (legacy support)."""
        if self._db is None:
            from astrapy import DataAPIClient

            self._client = DataAPIClient()
            self._db = self._client.get_database(
                api_endpoint=self.astra_endpoint, token=self.astra_token, keyspace=self.astra_keyspace
            )
        return self._db

    def validate_config(self):
        """Validate that required configuration is present based on the selected provider."""
        missing_vars = []

        # Always require OpenAI API key
        if not self.openai_api_key:
            missing_vars.append("OPENAI_API_KEY")

        # Validate provider-specific configuration
        if self.database_provider == "astra":
            if not self.astra_token:
                missing_vars.append("ASTRADB_TOKEN")
        elif self.database_provider == "azure":
            if not self.azure_search_endpoint:
                missing_vars.append("AZURE_SEARCH_ENDPOINT")
            if not self.azure_search_key:
                missing_vars.append("AZURE_SEARCH_KEY")
        else:
            missing_vars.append(f"Unknown DATABASE_PROVIDER: {self.database_provider}")

        if missing_vars:
            raise ValueError(f"Missing required configuration for {self.database_provider}: {', '.join(missing_vars)}")

    def get_database_config(self) -> dict:
        """Get database configuration for the current provider."""
        if self.database_provider == "astra":
            return {
                "astra_endpoint": self.astra_endpoint,
                "astra_token": self.astra_token,
                "keyspace": self.astra_keyspace,
            }
        elif self.database_provider == "azure":
            return {
                "search_endpoint": self.azure_search_endpoint,
                "search_key": self.azure_search_key,
                "search_api_version": self.azure_search_api_version,
            }
        else:
            return {}


# Global configuration instance
config = Config()
