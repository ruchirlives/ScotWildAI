"""
Factory for creating database service instances based on configuration.
"""

import os
import logging
from typing import Union
from database_interface import DatabaseServiceInterface
from astra_database_service import AstraDBService
from azure_database_service import AzureSearchService

logger = logging.getLogger(__name__)


class DatabaseServiceFactory:
    """Factory for creating database service instances."""

    SUPPORTED_PROVIDERS = {
        "astra": AstraDBService,
        "azure": AzureSearchService,
    }

    @classmethod
    def create_service(cls, provider: str = None, **kwargs) -> DatabaseServiceInterface:
        """
        Create a database service instance based on the provider.

        Args:
            provider: The database provider ('astra' or 'azure').
                     If not specified, will try to determine from environment variables.
            **kwargs: Additional arguments for the specific service implementation.

        Returns:
            A database service instance implementing DatabaseServiceInterface.

        Raises:
            ValueError: If the provider is not supported or configuration is missing.
        """
        # Auto-detect provider if not specified
        if provider is None:
            provider = cls._detect_provider()

        provider = provider.lower()

        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported database provider: {provider}. "
                f"Supported providers: {list(cls.SUPPORTED_PROVIDERS.keys())}"
            )

        service_class = cls.SUPPORTED_PROVIDERS[provider]

        try:
            if provider == "astra":
                return cls._create_astra_service(**kwargs)
            elif provider == "azure":
                return cls._create_azure_service(**kwargs)
        except Exception as e:
            logger.error(f"Failed to create {provider} database service: {e}")
            raise

    @classmethod
    def _detect_provider(cls) -> str:
        """
        Auto-detect the database provider based on environment variables.

        Returns:
            The detected provider name.
        """
        # Check for Astra DB configuration
        if os.getenv("ASTRADB_TOKEN") and os.getenv("ASTRADB_ENDPOINT"):
            logger.info("Detected Astra DB configuration")
            return "astra"

        # Check for Azure Search configuration
        if os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_SEARCH_KEY"):
            logger.info("Detected Azure Search configuration")
            return "azure"

        # Default to environment variable if set
        provider = os.getenv("DATABASE_PROVIDER", "astra").lower()
        logger.info(f"Using DATABASE_PROVIDER environment variable: {provider}")
        return provider

    @classmethod
    def _create_astra_service(cls, **kwargs) -> AstraDBService:
        """Create an Astra DB service instance."""
        astra_endpoint = kwargs.get("astra_endpoint") or os.getenv("ASTRADB_ENDPOINT")
        astra_token = kwargs.get("astra_token") or os.getenv("ASTRADB_TOKEN")
        keyspace = kwargs.get("keyspace") or os.getenv("ASTRADB_KEYSPACE", "default_keyspace")

        if not astra_endpoint:
            raise ValueError("Astra DB endpoint is required but not found in environment variables")

        if not astra_token:
            raise ValueError("Astra DB token is required but not found in environment variables")

        return AstraDBService(astra_endpoint=astra_endpoint, astra_token=astra_token, keyspace=keyspace)

    @classmethod
    def _create_azure_service(cls, **kwargs) -> AzureSearchService:
        """Create an Azure Search service instance."""
        search_endpoint = kwargs.get("search_endpoint") or os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = kwargs.get("search_key") or os.getenv("AZURE_SEARCH_KEY")
        search_api_version = kwargs.get("search_api_version", "2023-11-01")

        return AzureSearchService(
            search_endpoint=search_endpoint, search_key=search_key, search_api_version=search_api_version
        )


class DatabaseServiceRegistry:
    """Registry to manage database service instances with singleton pattern."""

    _instance = None
    _service = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_service(self, provider: str = None, **kwargs) -> DatabaseServiceInterface:
        """
        Get a database service instance, creating it if it doesn't exist.

        Args:
            provider: The database provider.
            **kwargs: Additional arguments for service creation.

        Returns:
            A database service instance.
        """
        if self._service is None:
            self._service = DatabaseServiceFactory.create_service(provider, **kwargs)
        return self._service

    def switch_provider(self, provider: str, **kwargs) -> DatabaseServiceInterface:
        """
        Switch to a different database provider.

        Args:
            provider: The new database provider.
            **kwargs: Additional arguments for service creation.

        Returns:
            The new database service instance.
        """
        # Close existing connection if it exists
        if self._service:
            try:
                self._service.close_connection()
            except Exception as e:
                logger.warning(f"Error closing existing database connection: {e}")

        # Create new service
        self._service = DatabaseServiceFactory.create_service(provider, **kwargs)
        logger.info(f"Switched to {provider} database provider")
        return self._service

    def reset(self):
        """Reset the registry (useful for testing)."""
        if self._service:
            try:
                self._service.close_connection()
            except Exception as e:
                logger.warning(f"Error closing database connection during reset: {e}")
        self._service = None


# Global registry instance
database_registry = DatabaseServiceRegistry()
