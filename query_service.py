"""
Query processing services for different types of queries.
"""

import ast
from typing import List, Dict, Any
from openai_service import openai_service
from database_service import database_service
from text_formatter import text_formatter
from neo4j_handler import Neo4jHandler


class QueryService:
    """Service for processing different types of queries."""

    def get_visitor_context(self, query: str) -> str:
        """Get visitor evidence context for a query."""
        vector_context = database_service.get_visitor_evidence_context(query)
        formatted_context = text_formatter.format_context_items(vector_context, "visitor_evidence")

        context = f"Evidence base:\n{formatted_context}\n\n"
        return context

    def get_graph_context(self, query: str) -> str:
        """Get graph context using Neo4j."""
        neo4j_handler = Neo4jHandler()
        result = neo4j_handler.graph_rag(query)
        neo4j_handler.close()

        return text_formatter.format_graph_results(result)

    def get_evidence_summary(self, context: str) -> str:
        """Generate a summary of evidence sources."""
        question = (
            "Please provide a high level summary of the nature of the evidence sources "
            "available listed in the context. What kind of sources are these and how "
            "reliable are they likely to be? Limit your response to 120 words, "
            f"using UK English (en-gb):\n\nContext: {context}"
        )

        messages = [{"role": "user", "content": question}]
        return openai_service.generate_completion(messages)

    def summarise_message(self, message: str) -> str:
        """Summarise a message for clarity."""
        question = (
            "Please summarise the following message in a clear and concise manner in less than 40 words, "
            "using UK English (en-gb):\n\nMessage: {message}"
        ).format(message=message)

        messages = [{"role": "user", "content": question}]
        return openai_service.generate_completion(messages)

    def process_visitor_query(self, query: str) -> str:
        """Process a visitor-focused query."""
        question = (
            "Review the context and provide a concise, integrated, neutral and "
            "balanced response to the Query, strictly adhering to the context provided, "
            "and using simple language and written for an internal management audience. "
            f"Limit your response to 300 words, using UK English:\n\nQuery: {query}"
        )

        context = self.get_visitor_context(query)
        prompt = f"{question}\n\nAssertions:{context}"

        messages = [{"role": "user", "content": prompt}]
        text = openai_service.generate_completion(messages)

        evidence_summary = self.get_evidence_summary(context)
        full_response = (
            f"<div class='analysis-section'>"
            f"<h2 class='text-xl font-bold'>Analysis</h2>"
            f"<p>{text}</p>"
            f"</div>"
            f"<div class='evidence-summary-section mt-4'>"
            f"<h2 class='text-xl font-bold'>Evidence Summary</h2>"
            f"<p>{evidence_summary}</p>"
            f"</div>"
            f"<div class='sources-section mt-4'>"
            f"<h2 class='text-xl font-bold'>Sources</h2>"
            f"<p>{context}</p>"
            f"</div>"
        )

        return text_formatter.format_to_html(full_response)

    def process_enquiry(self, query: str) -> str:
        """Process a general enquiry."""
        question = (
            "Your role is to answer the query by providing a clear and concise response "
            "in less than 200 words and drawing exclusively from the Context, and explain "
            "how it is drawn from the context or just related to the context. Please use "
            "UK English spelling. List the most relevant sources, including the year and "
            "source with a URL. The blog should be clear, informative, and suitable for "
            "a general audience. Use straightforward language and avoid overly formal or "
            f"dramatic terms. Make sure the arguments are balanced and include references. en-gb:\n\nQuery: {query}"
        )

        blog_assertions = database_service.get_blog_assertions(query)
        prompt = f"{question}\n\nContext: {blog_assertions}"

        messages = [{"role": "user", "content": prompt}]
        text = openai_service.generate_completion(messages)

        return text_formatter.format_to_html(text)

    def break_down_query(self, query: str) -> List[Dict[str, str]]:
        """Break down a query into constituent components."""
        question = (
            "Your role is to break down the query into its constituent parts. "
            "Please only output a json formatted list of the main components of the query "
            "in the format [{'component':item}]. Use UK English spelling. "
            f"en-gb:\n\nQuery: {query}"
        )

        messages = [{"role": "user", "content": question}]
        text = openai_service.generate_completion(messages)

        return ast.literal_eval(text)

    def process_advanced_query(self, query: str) -> str:
        """Process an advanced query using component breakdown."""
        components = self.break_down_query(query)
        full_context = []

        for component in components:
            context = database_service.get_policy_assertions(component["component"], limit=15)
            full_context.extend(context)

        question = f"Please answer the query using the context. en-gb:\n\nQuery: {query}\n\nContext: {full_context}"

        messages = [{"role": "user", "content": question}]
        return openai_service.generate_completion(messages)

    def process_policy_query(self, query: str) -> str:
        """Process a policy-focused query."""
        question = (
            "You are a policy assistant responding to requests by highlighting the "
            "Scottish Wildlife Trust's policy assertions. You responses always use UK "
            "English spelling and always refer to the Scottish Wildlife Trust as the "
            "Trust or its full name, never as SWT. Please answer the following query "
            "based on the provided policy assertions, by providing a summary analysis "
            "followed by a table format list of the relevant assertions and the Name "
            "of their source (with its web link), and the source's Year and page number:"
            f"\n\n{query}"
        )

        vector_context = database_service.get_policy_assertions(query)
        formatted_context = text_formatter.format_context_items(vector_context, "policy_assertions")

        prompt = f"{question}\n\nPolicy assertions:{formatted_context}"

        messages = [{"role": "user", "content": prompt}]
        text = openai_service.generate_completion(messages)

        return text_formatter.format_to_html(text)

    def write_blog(self, query: str) -> str:
        """Write a blog post based on the query."""
        assertions_cursor = database_service.get_blog_assertions(query)
        policies_cursor = database_service.get_policy_assertions(query)

        # Convert cursors to lists
        assertions = list(assertions_cursor)
        policies = list(policies_cursor)

        content = (
            "Please write a 400-word blog post with an engaging title in response to "
            "the following query. Use en-gb spelling throughout. Ensure any evidence "
            "referenced is accurately reflected in the provided assertions, including "
            "the year and source with a URL. The blog should be clear, informative, "
            "and suitable for a general audience. Use straightforward language and "
            "avoid overly formal or dramatic terms. Make sure the arguments are "
            f"balanced and include references. \n\nQuery: {query}\n\nAssertions: {assertions}"
            f"\n\nPolicy Assertions: {policies}"
        )

        messages = [{"role": "user", "content": content}]
        text = openai_service.generate_completion(messages)

        return text_formatter.format_to_html(text)

    def tag_summary(self, summary: str) -> str:
        """Generate a tag for a given summary."""
        question = (
            "Please generate a concise and relevant tag for the following summary. "
            "The tag should be up to two single words, separated by commas that captures the essence of the summary. "
            "For example, conservation, policy, operations, academic, digital, staff development etc. "
            "Use UK English spelling.\n\nSummary: {summary}"
        ).format(summary=summary)

        messages = [{"role": "user", "content": question}]
        return openai_service.generate_completion(messages)


# Global service instance
query_service = QueryService()
