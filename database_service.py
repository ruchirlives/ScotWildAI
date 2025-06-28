"""
Database services for interacting with different database providers.
This module provides a unified interface that can work with Astra DB or Azure Search.
"""

from database_factory import database_registry
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Unified database service that delegates to the appropriate provider.
    This maintains backwards compatibility while enabling provider switching.
    """

    def __init__(self, provider: str = None, **kwargs):
        """
        Initialize the database service with a specific provider.

        Args:
            provider: Database provider ('astra' or 'azure'). If None, auto-detects.
            **kwargs: Additional configuration for the specific provider.
        """
        self._service = database_registry.get_service(provider, **kwargs)

    def switch_provider(self, provider: str, **kwargs):
        """
        Switch to a different database provider.

        Args:
            provider: The new database provider to use.
            **kwargs: Additional configuration for the new provider.
        """
        self._service = database_registry.switch_provider(provider, **kwargs)
        logger.info(f"Database service switched to {provider}")

    def get_current_provider(self) -> str:
        """Get the name of the current database provider."""
        return self._service.__class__.__name__

    def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        return self._service.health_check()

    def get_visitor_evidence_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get visitor evidence context from vector search."""
        return self._service.get_visitor_evidence_context(query, limit)

    def get_policy_assertions(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Get policy assertions from vector search."""
        return self._service.get_policy_assertions(query, limit)

    def get_blog_assertions(self, query: str, limit: int = 18) -> List[Dict[str, Any]]:
        """Get related blog assertions."""
        return self._service.get_blog_assertions(query, limit)


# Global service instance
database_service = DatabaseService()
