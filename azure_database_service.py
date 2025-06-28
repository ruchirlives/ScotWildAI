"""
Azure Cognitive Search implementation of the database service interface.
"""

from typing import List, Dict, Any
import logging
import os
from database_interface import DatabaseServiceInterface
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AzureSearchService(DatabaseServiceInterface):
    """Azure Cognitive Search implementation of database service."""

    # Define class variable for fields to select
    FIELDS = ["id", "message", "summary", "uploadDate", "tag", "url"]

    def __init__(self, search_endpoint: str = None, search_key: str = None, search_api_version: str = "2023-11-01"):
        self.search_endpoint = search_endpoint or os.getenv("AZURE_SEARCH_ENDPOINT")
        self.search_key = search_key or os.getenv("AZURE_SEARCH_KEY")
        self.search_api_version = search_api_version
        self._client = None
        self.initialize_connection()

    def initialize_connection(self) -> None:
        """Initialize the Azure Cognitive Search connection."""
        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential

            if not self.search_endpoint or not self.search_key:
                raise ValueError("Azure Search endpoint and key must be provided")

            # Initialize with a default index, can be changed per operation
            self._credential = AzureKeyCredential(self.search_key)
            logger.info("Azure Search connection initialized successfully")
        except ImportError:
            logger.error("Azure Search SDK not installed. Install with: pip install azure-search-documents")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Azure Search connection: {e}")
            raise

    def _get_search_client(self, index_name: str):
        """Get a search client for a specific index."""
        from azure.search.documents import SearchClient

        return SearchClient(endpoint=self.search_endpoint, index_name=index_name, credential=self._credential)

    def close_connection(self) -> None:
        """Close the Azure Search connection if needed."""
        # Azure Search client doesn't require explicit closing
        logger.info("Azure Search connection closed")

    def health_check(self) -> bool:
        """Check if the Azure Search connection is healthy."""
        try:
            # Try to get service statistics as a health check
            from azure.search.documents.indexes import SearchIndexClient

            index_client = SearchIndexClient(endpoint=self.search_endpoint, credential=self._credential)
            stats = index_client.get_service_statistics()
            return True
        except Exception as e:
            logger.error(f"Azure Search health check failed: {e}")
            return False

    def get_visitor_evidence_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Not implemented for Azure Search - use get_message_descriptions instead."""
        logger.warning("get_visitor_evidence_context not implemented for Azure Search")
        return []

    def get_policy_assertions(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Not implemented for Azure Search - use get_message_descriptions instead."""
        logger.warning("get_policy_assertions not implemented for Azure Search")
        return []

    def get_blog_assertions(self, query: str, limit: int = 18) -> List[Dict[str, Any]]:
        """Not implemented for Azure Search - use get_message_descriptions instead."""
        logger.warning("get_blog_assertions not implemented for Azure Search")
        return []

    def _format_results_as_table(self, results) -> str:
        """Format search results as an HTML table with Tailwind CSS styling and hyperlink for ID."""
        table_rows = []
        for result in results:
            doc_id = result.get("id", "")
            summary = result.get("summary", "")
            upload_date = result.get("uploadDate", "")
            tag = result.get("tag", "")
            url = result.get("url", "#")  # Default to '#' if URL is not provided
            try:
                # Format the date as Day, Date, Time
                formatted_date = datetime.fromisoformat(upload_date).strftime("%A, %d %B %Y, %I:%M %p")
            except ValueError:
                formatted_date = upload_date  # Keep original if parsing fails
            table_rows.append(
                f"<tr class='border-b'>"
                f"<td class='px-4 py-2'>{formatted_date}</td>"
                f"<td class='px-4 py-2'>{summary}</td>"
                f"<td class='px-4 py-2'>{tag}</td>"
                f"<td class='px-4 py-2'>"
                f"<a href='{url}' class='text-blue-500 underline' target='_blank'>{doc_id}</a>"
                f"</td>"
                f"</tr>"
            )

        # Add Tailwind CSS CDN reference
        tailwind_cdn = (
            "<link href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css' rel='stylesheet'>"
        )

        # Create an HTML table with Tailwind classes
        table_html = f"""
        {tailwind_cdn}
        <div class='overflow-x-auto'>
            <table class='min-w-full bg-white border border-gray-200'>
                <thead class='bg-gray-100'>
                    <tr>
                        <th class='px-4 py-2 border-b'>Date</th>
                        <th class='px-4 py-2 border-b'>Summary</th>
                        <th class='px-4 py-2 border-b'>Tag</th>
                        <th class='px-4 py-2 border-b'>ID</th>
                    </tr>
                </thead>
                <tbody>
        """
        table_html += "".join(table_rows)
        table_html += "</tbody></table></div>"

        return table_html

    def get_message_descriptions(self, query: str, limit: int = 10) -> str:
        """Get message descriptions from vector search using Azure Cognitive Search."""
        try:
            from openai_service import openai_service

            embedding = openai_service.get_embeddings(query)
            search_client = self._get_search_client("messages")  # or your actual index name

            # Use the class variable for fields
            fields = self.FIELDS

            # Perform vector search using Azure Cognitive Search
            from azure.search.documents.models import VectorizedQuery

            vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=limit, fields="content_vector")

            results = search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=fields,
                top=limit,
            )

            # Directly format results as a table
            return self._format_results_as_table(results)
        except Exception as e:
            logger.error(f"Error getting message descriptions from Azure: {e}")
            return "<p>Error retrieving messages.</p>"

    def upload_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to the specified index/collection."""
        from query_service import query_service

        if not documents:
            logger.warning("No documents provided for upload")
            return False
        # Vectorise the documents if necessary
        for doc in documents:
            if "content_vector" not in doc:
                try:
                    from openai_service import openai_service

                    doc["content_vector"] = openai_service.get_embeddings(doc.get("content", ""))
                except Exception as e:
                    logger.error(f"Failed to vectorize document: {e}")
                    return False

            if doc["summary"] == "":
                doc["summary"] = query_service.summarise_message(doc.get("message", ""))

            if doc["tag"] == "":
                doc["tag"] = query_service.tag_summary(doc.get("summary", ""))
        try:
            client = self._get_search_client(index_name)
            result = client.upload_documents(documents=documents)
            logger.info(f"Uploaded {len(result)} documents to {index_name}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    def delete_all_documents(self, index_name: str) -> bool:
        """Delete all documents in the specified index."""
        try:
            client = self._get_search_client(index_name)
            client.delete_documents(documents=[{"id": doc["id"]} for doc in client.search("*")])
            logger.info(f"Deleted all documents from {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete documents from {index_name}: {e}")
            return False

    def delete_document_by_id(self, index_name: str, document_id: str) -> bool:
        """Delete a specific document by its ID from the specified index."""
        try:
            client = self._get_search_client(index_name)
            client.delete_documents(documents=[{"id": document_id}])
            logger.info(f"Deleted document with ID {document_id} from {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document with ID {document_id} from {index_name}: {e}")
            return False

    def get_messages_since(self, since_date: datetime, return_format="html") -> str:
        """Get messages uploaded since the given date."""
        try:
            search_client = self._get_search_client("messages")

            # Convert since_date to UTC
            since_date_utc = since_date.astimezone(timezone.utc)

            # Use the class variable for fields
            fields = self.FIELDS

            # Perform a search query to filter messages by uploadDate
            results = search_client.search(
                search_text=None,
                filter=f"uploadDate ge {since_date_utc.isoformat()}",
                select=fields,
            )

            # Convert Azure Search results to a list of dictionaries and sort by score in descending order
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "id": result.get("id", ""),
                        "summary": result.get("summary", ""),
                        "uploadDate": result.get("uploadDate", ""),
                        "tag": result.get("tag", ""),
                        "url": result.get("url", ""),
                        "score": result.get("@search.score", 0),
                    }
                )

            # Sort results by score in descending order
            formatted_results.sort(key=lambda x: x["score"], reverse=True)

            # If a specific return format is requested, use it
            if return_format == "json":
                return formatted_results
            else:
                # Format sorted results as a table
                return self._format_results_as_table(formatted_results)
        except Exception as e:
            logger.error(f"Error getting messages since {since_date}: {e}")
            return "<p>Error retrieving messages.</p>"

    def retag_message(self, message_id: str) -> bool:
        """Retag a message in Azure Cognitive Search by ID."""
        try:
            # Fetch the message document by ID
            client = self._get_search_client("messages")
            document = client.get_document(key=message_id)

            if not document:
                logger.error(f"Message with ID {message_id} not found.")
                return False

            # Generate a new tag based on the summary
            from query_service import query_service
            new_tag = query_service.tag_summary(document.get("summary", ""))

            # Update the document with the new tag
            document["tag"] = new_tag
            client.merge_or_upload_documents(documents=[document])

            logger.info(f"Message with ID {message_id} retagged successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to retag message with ID {message_id}: {e}")
            return False

    def retag_all_messages(self) -> bool:
        """Retag all messages in Azure Cognitive Search."""
        try:
            client = self._get_search_client("messages")

            # Fetch all documents in the index
            results = client.search("*", select=self.FIELDS)

            documents_to_update = []

            for document in results:
                # Generate a new tag based on the summary
                from query_service import query_service
                new_tag = query_service.tag_summary(document.get("summary", ""))

                # Update the document with the new tag
                document["tag"] = new_tag
                documents_to_update.append(document)

            # Batch update all documents
            if documents_to_update:
                client.merge_or_upload_documents(documents=documents_to_update)

            logger.info("All messages retagged successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to retag all messages: {e}")
            return False
