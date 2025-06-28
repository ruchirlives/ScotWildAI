"""
Astra DB implementation of the database service interface.
"""

from typing import List, Dict, Any
import logging
from database_interface import DatabaseServiceInterface
from openai_service import openai_service
from datetime import datetime

logger = logging.getLogger(__name__)


class AstraDBService(DatabaseServiceInterface):
    """Astra DB implementation of database service."""

    def __init__(self, astra_endpoint: str, astra_token: str, keyspace: str = "default_keyspace"):
        self.astra_endpoint = astra_endpoint
        self.astra_token = astra_token
        self.keyspace = keyspace
        self._client = None
        self._db = None
        self.initialize_connection()

    def initialize_connection(self) -> None:
        """Initialize the Astra DB connection."""
        try:
            from astrapy import DataAPIClient

            self._client = DataAPIClient()
            self._db = self._client.get_database(
                api_endpoint=self.astra_endpoint, token=self.astra_token, keyspace=self.keyspace
            )
            logger.info("Astra DB connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Astra DB connection: {e}")
            raise

    def close_connection(self) -> None:
        """Close the Astra DB connection if needed."""
        # Astra DB client doesn't require explicit closing
        logger.info("Astra DB connection closed")

    def health_check(self) -> bool:
        """Check if the Astra DB connection is healthy."""
        try:
            # Try to list collections as a health check
            collections = self._db.list_collection_names()
            return True
        except Exception as e:
            logger.error(f"Astra DB health check failed: {e}")
            return False

    def get_visitor_evidence_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get visitor evidence context from vector search."""
        try:
            embedding = openai_service.get_embeddings(query)
            collection = self._db.get_collection("visitorevidence")

            # Perform a vector similarity search
            results = collection.find(
                sort={"$vector": embedding},
                limit=limit,
                projection={"Name": 1, "PolicyAssertion": 1, "Evidence": 1, "Year": 1},
                include_similarity=True,
            )

            return list(results)
        except Exception as e:
            logger.error(f"Error getting visitor evidence context: {e}")
            return []

    def get_policy_assertions(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Get policy assertions from vector search."""
        try:
            collection = self._db.get_collection("assertions")
            embedding = openai_service.get_embeddings(query)

            results = collection.find(
                sort={"$vector": embedding},
                limit=limit,
                projection={"Name", "PolicyAssertion", "Page", "Year", "Link"},
                include_similarity=True,
            )

            return list(results)
        except Exception as e:
            logger.error(f"Error getting policy assertions: {e}")
            return []

    def get_blog_assertions(self, query: str, limit: int = 18) -> List[Dict[str, Any]]:
        """Get related blog assertions."""
        try:
            collection = self._db.get_collection("blogs")
            assertions_cursor = collection.find(sort={"$vectorize": query})

            # Convert the cursor to a list of documents
            assertions = list(assertions_cursor)

            return assertions[:limit]
        except Exception as e:
            logger.error(f"Error getting blog assertions: {e}")
            return []

    def upload_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to the specified index/collection."""
        try:
            collection = self._db.get_collection(index_name)
            result = collection.insert_many(documents)
            logger.info(f"Uploaded {len(documents)} documents to {index_name}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    def get_message_descriptions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get message descriptions - not implemented for Astra DB."""
        logger.warning("get_message_descriptions not implemented for Astra DB")
        return []

    def get_messages_since(self, since_date: datetime) -> List[Dict[str, Any]]:
        """Dummy implementation for AstraDBService."""
        logger.warning("get_messages_since is not implemented for AstraDBService.")
        return []

    def delete_document_by_id(self, index_name: str, document_id: str) -> bool:
        """Stub implementation for deleting a document by ID in AstraDBService."""
        logger.warning("delete_document_by_id is not implemented for AstraDBService.")
        return False
