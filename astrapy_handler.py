"""
Refactored Astra DB handler using modular services.

This module provides a simplified interface to the various services
for backwards compatibility with existing code.
"""

from config import config
from openai_service import openai_service
from database_service import database_service
from text_formatter import text_formatter
from query_service import query_service

# Backwards compatibility functions
def get_openai_client():
    """Get OpenAI client (backwards compatibility)."""
    return openai_service.get_client()

def get_vc_context(query: str, client=None) -> str:
    """Get visitor context (backwards compatibility)."""
    return query_service.get_visitor_context(query)

def get_vc_graph(query: str) -> str:
    """Get graph context (backwards compatibility)."""
    return query_service.get_graph_context(query)

def get_evidence_summary(context: str) -> str:
    """Get evidence summary (backwards compatibility)."""
    return query_service.get_evidence_summary(context)

def get_vc_query(query: str) -> str:
    """Process visitor query (backwards compatibility)."""
    return query_service.process_visitor_query(query)

def get_enquiry(query: str) -> str:
    """Process enquiry (backwards compatibility)."""
    return query_service.process_enquiry(query)

def break_down_query(query: str) -> str:
    """Break down query (backwards compatibility)."""
    return query_service.break_down_query(query)

def advanced_query(query: str) -> str:
    """Process advanced query (backwards compatibility)."""
    return query_service.process_advanced_query(query)

def get_policy_query(query: str) -> str:
    """Process policy query (backwards compatibility)."""
    return query_service.process_policy_query(query)

def get_policy_context(query: str, limit=8) -> str:
    """Get policy context (backwards compatibility)."""
    return database_service.get_policy_assertions(query, limit)

def get_embeddings(query, client=None):
    """Get embeddings (backwards compatibility)."""
    return openai_service.get_embeddings(query)

def getRelatedBlogAssertions(query, collection=None):
    """Get related blog assertions (backwards compatibility)."""
    return database_service.get_blog_assertions(query)

def writeBlog(query: str):
    """Write blog (backwards compatibility)."""
    return query_service.write_blog(query)

def format_text(text: str) -> str:
    """Format text (backwards compatibility)."""
    return text_formatter.format_to_html(text)

# Initialize configuration validation
try:
    config.validate_config()
except ValueError as e:
    print(f"Configuration warning: {e}")

# For testing purposes (uncommented from original)
if __name__ == "__main__":
    # query = "What is the Scottish Wildlife Trust's view of private sector engagement with natural capital?"
    # answer = advanced_query(query)
    # print(answer)
    # query = "Trust funds"
    # answer = get_vc_query(query)
    # print(answer)
    pass
