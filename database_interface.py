"""
Abstract base class for database services to enable swappable implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class DatabaseServiceInterface(ABC):
    """Abstract interface for database services."""

    @abstractmethod
    def get_visitor_evidence_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get visitor evidence context from vector search."""
        pass

    @abstractmethod
    def get_policy_assertions(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Get policy assertions from vector search."""
        pass

    @abstractmethod
    def get_blog_assertions(self, query: str, limit: int = 18) -> List[Dict[str, Any]]:
        """Get related blog assertions."""
        pass

    @abstractmethod
    def initialize_connection(self) -> None:
        """Initialize the database connection."""
        pass

    @abstractmethod
    def close_connection(self) -> None:
        """Close the database connection if needed."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        pass

    @abstractmethod
    def upload_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to the specified index/collection."""
        pass

    @abstractmethod
    def get_message_descriptions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get message descriptions from vector search."""
        pass

    @abstractmethod
    def get_messages_since(self, since_date: datetime, return_format="html") -> List[Dict[str, Any]]:
        """Get messages uploaded since the given date."""
        pass

    @abstractmethod
    def delete_document_by_id(self, index_name: str, document_id: str) -> bool:
        """Delete a specific document by its ID from the specified index."""
        pass
