"""
Text formatting utilities.
"""

import markdown


class TextFormatter:
    """Utility class for text formatting operations."""

    @staticmethod
    def format_to_html(text: str) -> str:
        """Convert markdown text to HTML with improved Tailwind CSS styling."""
        html = markdown.markdown(text, extensions=["markdown.extensions.tables"])
        # Replace \n with <br> to maintain line breaks, but avoid adding extra gaps
        html = html.replace("\n", "")

        # Post-process the HTML to inject Tailwind classes into tables
        html = html.replace("<table>", "<br><table class='table-auto border-collapse border border-gray-300'>")
        html = html.replace("<th>", "<th class='border border-gray-300 bg-gray-100 px-4 py-2 text-left'>")
        html = html.replace("<td>", "<td class='border border-gray-300 px-4 py-2'>")

        # Add Tailwind CSS CDN reference
        tailwind_cdn = (
            "<link href='https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css' rel='stylesheet'>"
        )

        # Wrap the HTML in a styled container using enhanced Tailwind CSS classes
        styled_html = (
            f"{tailwind_cdn}"
            "<div class='prose max-w-none bg-gradient-to-r from-blue-50 to-blue-100 "
            "p-12 rounded-2xl shadow-xl hover:shadow-2xl transition-shadow duration-300 border border-blue-200'>"
            f"{html}"
            "</div>"
        )
        return styled_html

    @staticmethod
    def format_context_items(items: list, format_type: str = "visitor_evidence") -> str:
        """Format context items into a readable string with Tailwind CSS styling."""
        if format_type == "visitor_evidence":
            formatted_items = "<ul>" + "".join(
                [
                    f"<li>"
                    f"<strong>{item['Name']}</strong> - "
                    f"Assertion: {item['PolicyAssertion']} - "
                    f"[Evidence: <span>{item['Evidence']}</span>] - "
                    f"<span>{item['Year']}</span></li>"
                    for item in items
                ]
            ) + "</ul>"
        elif format_type == "policy_assertions":
            formatted_items = "<ul>" + "".join(
                [
                    f"<li>"
                    f"Assertion: <span>{item['PolicyAssertion']}</span> - "
                    f"Source: <strong>{item['Name']}</strong> - "
                    f"Year: <span>{item['Year']}</span> - "
                    f"Page: <span>{item['Page']}</span> - "
                    f"Link: <a href='{item['Link']}'>{item['Link']}</a></li>"
                    for item in items
                ]
            ) + "</ul>"
        else:
            formatted_items = f"<div>{str(items)}</div>"

        return formatted_items

    @staticmethod
    def format_graph_results(results: list) -> str:
        """Format graph query results into a readable string."""
        answer = ""
        for item in results:
            relationship_info = (
                f"{item['n.name']} - {item['r.Relationship']} - {item['m.name']} "
                f"(Criticality: {item['r.Criticality']})"
            )
            answer += f"{relationship_info}\n{item['r.`Evidence base`']}\n\n"
        return answer


# Global formatter instance
text_formatter = TextFormatter()
