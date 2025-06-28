# ScotWild AI - Intelligent Knowledge Management System

ScotWild AI is a Flask-based application designed to enhance organizational knowledge management through intelligent search, content generation, and document processing. Powered by AI and vector search, it provides fast, accurate, and contextually relevant insights.

## 🚀 Features

### Intelligent Query System

- **Policy Queries**: Search and analyze organizational policies.

- **Visitor Evidence Search**: Retrieve relevant visitor evidence and case studies.

- **General Enquiries**: Answer questions using your knowledge base.

- **Blog Generation**: Create AI-powered content based on your data.

### Document Processing

- **Word Document Enhancement**: Automatically enhance Word documents with organizational data.

- **SharePoint Integration**: Process documents with SharePoint list data.

- **Dynamic Content Generation**: Generate contextually relevant document content.

### Advanced Search Capabilities

- **Vector Search**: Perform semantic searches using OpenAI embeddings.

- **Multi-Database Support**: Seamlessly switch between Astra DB and Azure Cognitive Search.

- **Real-time Results**: Get fast and accurate responses powered by AI.

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **AI/ML**: OpenAI GPT models and embeddings
- **Databases**: DataStax Astra DB, Azure Cognitive Search
- **Document Processing**: python-docx
- **Graph Database**: Neo4j (optional)
- **Deployment**: Google Cloud Run, Docker

## 📋 API Endpoints

| Endpoint               | Method | Description                                | Database       |
|------------------------|--------|--------------------------------------------|----------------|
| `/enquiries`           | POST   | General knowledge base queries            | Configurable   |
| `/policyquery`         | POST   | Search organizational policies            | Configurable   |
| `/visitorevidence`     | POST   | Retrieve visitor evidence and case studies| Configurable   |
| `/blog`                | POST   | Generate blog content                     | Configurable   |
| `/messages`            | POST   | Search message descriptions               | Azure Search   |
| `/health`              | GET    | Check database service health status      | Both           |
| `/search`              | POST   | Generic search using configured provider  | Configurable   |
| `/wordify`             | POST   | Enhance Word documents                    | Both           |
| `/add_message`         | POST   | Add a message document                    | Azure Search   |
| `/delete_messages`     | DELETE | Delete all messages                       | Azure Search   |
| `/get_recent_messages` | GET    | Get recent messages uploaded              | Azure Search   |
| `/delete_message`      | GET    | Delete a specific message by ID           | Azure Search   |
| `/retag`               | GET    | Retag all messages                        | Azure Search   |

## 🚦 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Database provider (Astra DB or Azure Cognitive Search)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd ScotWildAI
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**

   ```bash
   copy .env.example .env
   ```

   Edit `.env` with your API keys and database credentials.

4. **Run the application**

   ```bash
   python app.py
   ```

## ⚙️ Configuration

Copy the example environment file and configure your settings:

```bash
copy .env.example .env
```

Edit `.env` with your actual values. Key environment variables include:

```bash
OPENAI_API_KEY=your_openai_api_key
ASTRADB_TOKEN=your_astra_db_token
GCLOUD_PROJECT_ID=your_google_cloud_project_id
```

## 📚 Usage Examples

### API Usage

```python
import requests

# Policy query
response = requests.post("http://localhost:5000/policyquery", 
                        json={"query": "What is our environmental policy?"})

# Blog generation
response = requests.post("http://localhost:5000/blog", 
                        json={"query": "sustainable practices"})
```

### Direct Service Usage

```python
from query_service import query_service

# Search policies
result = query_service.process_policy_query("environmental policy")

# Generate content
blog_post = query_service.write_blog("sustainability practices")
```

## 🔧 Dependencies

- `openai` - OpenAI API client
- `astrapy` - Astra DB integration
- `flask` - Web framework
- `python-docx` - Word document processing
- `neo4j` - Graph database (optional)

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions, including:

- Google Cloud Run deployment
- Docker containerization
- Environment configuration
- CI/CD with Cloud Build

## 📖 Additional Documentation

- [Database Switching Guide](DATABASE_SWITCHING_GUIDE.md) - How to switch between Astra DB and Azure Search
- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions

## 🔮 Future Enhancements

- Add new query types
- Support additional database backends
- Enhance caching mechanisms
- Improve logging and monitoring

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
