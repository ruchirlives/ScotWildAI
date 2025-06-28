import re
from flask import Blueprint, current_app, request, send_file
from word import revised_document
import base64
from database_factory import DatabaseServiceFactory
from config import config
from query_service import query_service
from functools import wraps

# This is the path to the directory where you want to save the uploaded files.
# Make sure this directory exists on your server.

app = current_app
routes_bp = Blueprint("vectorsearch", __name__)


# Initialize database services based on configuration
def get_astra_service():
    """Get Astra service instance."""
    return DatabaseServiceFactory.create_service("astra")


def get_azure_service():
    """Get Azure service instance."""
    return DatabaseServiceFactory.create_service("azure")


def get_current_service():
    """Get the currently configured database service."""
    provider = config.database_provider.lower()
    if provider == "azure":
        return get_azure_service()
    else:  # default to astra
        return get_astra_service()


def set_current_service(service):
    """Set the current service instance."""
    global query_service
    if service.lower() == "azure":
        query_service = DatabaseServiceFactory.create_service("azure")
    elif service.lower() == "astra":
        query_service = DatabaseServiceFactory.create_service("astra")
    else:
        raise ValueError(f"Unsupported service: {service}. Supported services are 'azure' and 'astra'.")


# Middleware to check API key
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if api_key != config.api_key:
            return {"error": "Unauthorized: Invalid API key"}, 401
        return f(*args, **kwargs)
    return decorated_function


@routes_bp.route("/enquiries", methods=["POST"])
@require_api_key
def enquiries():
    """Handle general enquiries using Astra only."""
    try:
        if request.is_json:
            data = request.get_json()
            query = data.get("query")
        else:
            data = request.form
            query = request.form.get("query")

        if not query:
            return {"error": "Query parameter is required"}, 400

        response = query_service.process_enquiry(query)
        return response
    except Exception as e:
        return {"error": f"Failed to process enquiry: {str(e)}"}, 500


@routes_bp.route("/policyquery", methods=["POST"])
@require_api_key
def policyquery():
    """Handle policy queries using Astra only."""
    try:
        if request.is_json:
            data = request.get_json()
            query = data.get("query")
        else:
            data = request.form
            query = request.form.get("query")

        if not query:
            return {"error": "Query parameter is required"}, 400

        response = query_service.process_policy_query(query)
        return response

    except Exception as e:
        return {"error": f"Failed to process policy query: {str(e)}"}, 500


@routes_bp.route("/visitorevidence", methods=["POST"])
@require_api_key
def vcquery():
    """Handle visitor evidence queries using Astra only."""
    try:
        if request.is_json:
            data = request.get_json()
            query = data.get("query")
        else:
            data = request.form
            query = request.form.get("query")

        if not query:
            return {"error": "Query parameter is required"}, 400

        response = query_service.process_visitor_query(query)
        return response
    except Exception as e:
        return {"error": f"Failed to process visitor evidence query: {str(e)}"}, 500


@routes_bp.route("/blog", methods=["POST"])
@require_api_key
def blog():
    """Handle blog generation using Astra only."""
    try:
        if request.is_json:
            data = request.get_json()
            query = data.get("query")
        else:
            data = request.form
            query = request.form.get("query")

        if not query:
            return {"error": "Query parameter is required"}, 400

        response = query_service.write_blog(query)
        return response
    except Exception as e:
        return {"error": f"Failed to generate blog: {str(e)}"}, 500


@routes_bp.route("/messages", methods=["POST"])
@require_api_key
def messages():
    """Handle message queries using Azure only."""
    try:
        if request.is_json:
            data = request.get_json()
            query = data.get("query")
            limit = data.get("limit", 10)
            if limit == "":
                limit = 10
        else:
            data = request.form
            query = request.form.get("query")
            limit = request.form.get("limit", 10)
            if limit == "":
                limit = 10

        if not query:
            return {"error": "Query parameter is required"}, 400

        azure_service = get_azure_service()
        response = azure_service.get_message_descriptions(query, limit)
        return response
    except Exception as e:
        return {"error": f"Failed to search messages: {str(e)}"}, 500


@routes_bp.route("/health", methods=["GET"])
@require_api_key
def health():
    """Health check endpoint for database services."""
    try:
        astra_service = get_astra_service()
        azure_service = get_azure_service()

        astra_health = astra_service.health_check() if astra_service else False
        azure_health = azure_service.health_check() if azure_service else False

        return {
            "status": "ok" if (astra_health or azure_health) else "error",
            "services": {
                "astra": "healthy" if astra_health else "unhealthy",
                "azure": "healthy" if azure_health else "unhealthy",
            },
            "current_provider": config.database_provider,
        }
    except Exception as e:
        return {"error": f"Health check failed: {str(e)}"}, 500


@routes_bp.route("/search", methods=["POST"])
@require_api_key
def search():
    """Generic search endpoint that uses the currently configured database provider."""
    try:
        if request.is_json:
            data = request.get_json()
            query = data.get("query")
            limit = data.get("limit", 10)
        else:
            data = request.form
            query = request.form.get("query")
            limit = int(request.form.get("limit", 10))

        if not query:
            return {"error": "Query parameter is required"}, 400

        current_service = get_current_service()
        provider = config.database_provider.lower()

        # Use appropriate method based on provider
        if provider == "azure":
            results = current_service.get_message_descriptions(query, limit)
        else:  # astra
            # For Astra, we'll use a generic search (you can modify this based on your needs)
            results = current_service.get_policy_assertions(query)

        return {"query": query, "results": results, "count": len(results), "provider": provider}
    except Exception as e:
        return {"error": f"Failed to search: {str(e)}"}, 500


@routes_bp.route("/wordify", methods=["POST"])
@require_api_key
def wordify():
    if request.is_json:
        data = request.get_json()
        file = data.get("file")
        sharepoint_list = data.get("list")
        word_content_bytes = base64.b64decode(file)
        fake_file = revised_document(word_content_bytes, sharepoint_list)
    else:
        data = request.form
        file = request.files["file"]
        sharepoint_list = request.form.get("list")
        # convert sharepoint_list from string to a list of json objects

        # Read the file contents
        fake_file = revised_document(file.read(), sharepoint_list)

        # Create a response sending the DOCX file content
    return send_file(
        fake_file,
        as_attachment=True,
        download_name="generated_document.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@routes_bp.route("/add_message", methods=["POST"])
@require_api_key
def add_message():
    """Add a message document to Azure Cognitive Search."""
    import uuid

    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Required fields: message, id (generate if not provided)
        message = data.get("message")
        if not message:
            return {"error": "'message' field is required"}, 400

        doc_id = data.get("id") or str(uuid.uuid4())
        summary = data.get("summary", "")
        upload_date = data.get("uploadDate", "")
        url = data.get("url", "")
        tag = data.get("tag", "")

        # Generate content_vector from message
        from openai_service import openai_service

        try:
            content_vector = openai_service.get_embeddings(message)
        except Exception as e:
            return {"error": f"Failed to generate content_vector: {str(e)}"}, 500

        doc = {
            "id": doc_id,
            "message": message,
            "summary": summary,
            "uploadDate": upload_date,
            "url": url,
            "content_vector": content_vector,
            "tag": tag,
        }

        azure_service = get_azure_service()
        success = azure_service.upload_documents("messages", [doc])
        if success:
            return {"status": "success", "message": "Message uploaded to Azure Search.", "id": doc_id}
        else:
            return {"error": "Failed to upload message to Azure Search."}, 500
    except Exception as e:
        return {"error": f"Failed to add message: {str(e)}"}, 500


@routes_bp.route("/delete_messages", methods=["DELETE"])
@require_api_key
def delete_messages():
    """Delete all messages from Azure Cognitive Search."""
    try:
        azure_service = get_azure_service()
        success = azure_service.delete_all_documents("messages")
        if success:
            return {"status": "success", "message": "All messages deleted from Azure Search."}
        else:
            return {"error": "Failed to delete messages from Azure Search."}, 500
    except Exception as e:
        return {"error": f"Failed to delete messages: {str(e)}"}, 500


@routes_bp.route("/get_recent_messages", methods=["GET"])
@require_api_key
def get_recent_messages():
    """Get messages uploaded within the last x days."""
    from datetime import datetime, timedelta

    # Get the number of days from query parameters, default to 3 days
    days = request.args.get("days", 3, type=int)
    if days < 1:
        return {"error": "Days parameter must be at least 1"}, 400

    # Get the format of the return if specified, defaulting to html
    return_format = request.args.get("format", "html").lower()
    if return_format not in ["html", "json"]:
        return {"error": "Invalid format specified. Use 'html' or 'json'."}, 400

    try:
        azure_service = get_azure_service()
        startdate = datetime.now() - timedelta(days=3)
        recent_messages = azure_service.get_messages_since(startdate, return_format=return_format)

        if recent_messages:
            return recent_messages
        else:
            return []
    except Exception as e:
        return {"error": f"Failed to fetch recent messages: {str(e)}"}, 500


@routes_bp.route("/delete_message", methods=["GET"])
@require_api_key
def delete_message():
    """Delete a specific message from Azure Cognitive Search by ID."""
    try:
        # Get the message ID from query parameters
        message_id = request.args.get("id")
        if not message_id:
            return {"error": "Message ID is required."}, 400

        # Get the Azure service instance
        azure_service = get_azure_service()

        # Delete the specific message by ID
        success = azure_service.delete_document_by_id("messages", message_id)
        if success:
            return {"status": "success", "message": f"Message with ID {message_id} deleted from Azure Search."}
        else:
            return {"error": f"Failed to delete message with ID {message_id} from Azure Search."}, 500
    except Exception as e:
        return {"error": f"Failed to delete message: {str(e)}"}, 500


@routes_bp.route("/retag", methods=["GET"])
@require_api_key
def retag():
    """Handle retagging of all messages in Azure Cognitive Search."""
    try:
        azure_service = get_azure_service()
        success = azure_service.retag_all_messages()

        if success:
            return {"status": "success", "message": "All messages retagged successfully."}
        else:
            return {"error": "Failed to retag all messages."}, 500
    except Exception as e:
        return {"error": f"Failed to retag messages: {str(e)}"}, 500
