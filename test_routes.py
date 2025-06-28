from routes import get_azure_service
from openai_service import openai_service
import routes
from flask import Flask, request

class DummyAzureService:
    def upload_documents(self, index_name, documents):
        return True

def dummy_embeddings(message):
    return [0.1] * 1536  # same shape as real OpenAI vectors

def test_add_message_success(monkeypatch):
    monkeypatch.setattr("routes.get_azure_service", lambda: DummyAzureService())
    monkeypatch.setattr("openai_service.openai_service.get_embeddings", dummy_embeddings)

    app = Flask(__name__)
    app.register_blueprint(routes.routes_bp)
    client = app.test_client()

    data = {
        "message": "Test message",
        "summary": "Test summary",
        "uploadDate": "2025-06-27T12:00:00Z"
    }
    response = client.post("/add_message", json=data)
    assert response.status_code == 200
