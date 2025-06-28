# Database Provider Switching Guide

This guide explains how to switch between Astra DB and Azure Cognitive Search as your database provider.

## Overview

The application now supports multiple database providers through a swappable architecture:

- **Astra DB** (DataStax) - Vector database with built-in vector search
- **Azure Cognitive Search** - Microsoft's search service with vector search capabilities

## Configuration

### Environment Variables

Set the following environment variables based on your preferred provider:

#### For Astra DB (Default)
```bash
DATABASE_PROVIDER=astra
ASTRADB_TOKEN=AstraCS:...
ASTRADB_ENDPOINT=https://your-database-id-region.apps.astra.datastax.com
ASTRADB_KEYSPACE=default_keyspace  # Optional, defaults to "default_keyspace"
```

#### For Azure Cognitive Search
```bash
DATABASE_PROVIDER=azure
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-admin-key
AZURE_SEARCH_API_VERSION=2023-11-01  # Optional, defaults to "2023-11-01"
```

#### Always Required
```bash
OPENAI_API_KEY=sk-...  # Required for embedding generation
```

## Installation

### Base Installation
The base application works with Astra DB using existing dependencies.

### Azure Search Support
To use Azure Cognitive Search, install additional dependencies:

```bash
pip install -r requirements-azure.txt
```

Or manually:
```bash
pip install azure-search-documents azure-core
```

## Usage Examples

### Method 1: Environment Variable Configuration (Recommended)

Set your `DATABASE_PROVIDER` environment variable and restart your application:

```python
from database_service import database_service

# The service will automatically use the provider specified in DATABASE_PROVIDER
results = database_service.get_policy_assertions("environmental policy")
print(f"Using provider: {database_service.get_current_provider()}")
```

### Method 2: Programmatic Provider Switching

```python
from database_service import DatabaseService

# Create service with specific provider
db_service = DatabaseService(provider="azure")

# Or switch providers at runtime
db_service.switch_provider("astra")

# Check current provider
print(f"Current provider: {db_service.get_current_provider()}")

# Perform health check
if db_service.health_check():
    print("Database connection is healthy")
```

### Method 3: Direct Factory Usage

```python
from database_factory import DatabaseServiceFactory

# Create specific provider instances
astra_service = DatabaseServiceFactory.create_service("astra")
azure_service = DatabaseServiceFactory.create_service(
    "azure",
    search_endpoint="https://my-search.search.windows.net",
    search_key="my-key"
)
```

## Azure Search Index Setup

For Azure Cognitive Search to work properly, you need to create indexes with the following schemas:

### Visitor Evidence Index (`visitorevidence`)
```json
{
    "name": "visitorevidence",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": true},
        {"name": "Name", "type": "Edm.String", "searchable": true},
        {"name": "PolicyAssertion", "type": "Edm.String", "searchable": true},
        {"name": "Evidence", "type": "Edm.String", "searchable": true},
        {"name": "Year", "type": "Edm.String", "searchable": true},
        {
            "name": "content_vector",
            "type": "Collection(Edm.Single)",
            "searchable": true,
            "vectorSearchDimensions": 1536,
            "vectorSearchProfile": "default"
        }
    ]
}
```

### Policy Assertions Index (`assertions`)
```json
{
    "name": "assertions",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": true},
        {"name": "Name", "type": "Edm.String", "searchable": true},
        {"name": "PolicyAssertion", "type": "Edm.String", "searchable": true},
        {"name": "Page", "type": "Edm.String", "searchable": true},
        {"name": "Year", "type": "Edm.String", "searchable": true},
        {"name": "Link", "type": "Edm.String", "searchable": true},
        {
            "name": "content_vector",
            "type": "Collection(Edm.Single)",
            "searchable": true,
            "vectorSearchDimensions": 1536,
            "vectorSearchProfile": "default"
        }
    ]
}
```

### Blog Assertions Index (`blogs`)
```json
{
    "name": "blogs",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": true},
        {"name": "content", "type": "Edm.String", "searchable": true},
        {"name": "title", "type": "Edm.String", "searchable": true},
        {"name": "url", "type": "Edm.String", "searchable": true},
        {"name": "date", "type": "Edm.String", "searchable": true}
    ]
}
```

## Migration from Astra to Azure

1. **Set up Azure Search Service**
   - Create an Azure Cognitive Search service
   - Create the required indexes (see schemas above)
   - Migrate your data from Astra DB to Azure Search

2. **Update Environment Variables**
   ```bash
   DATABASE_PROVIDER=azure
   AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
   AZURE_SEARCH_KEY=your-admin-key
   ```

3. **Install Azure Dependencies**
   ```bash
   pip install -r requirements-azure.txt
   ```

4. **Switch Provider Dynamically**
   You can now change the `DATABASE_PROVIDER` environment variable and the application will use the new provider on the next request - **no restart required!**

## Current Route Behavior

### Provider-Aware Routes (Dynamic Switching)
All routes now dynamically switch based on the `DATABASE_PROVIDER` configuration:

- `/enquiries` → Uses Azure (message descriptions) or Astra (legacy enquiry function)
- `/policyquery` → Uses Azure (message descriptions) or Astra (policy assertions)
- `/visitorevidence` → Uses Azure (message descriptions) or Astra (visitor evidence context)
- `/blog` → Uses Azure (message descriptions) or Astra (blog assertions)
- `/messages` → **Always uses Azure Search** (message descriptions)
- `/search` → Uses the provider specified in `DATABASE_PROVIDER`
- `/health` → Checks both providers regardless of configuration

### Fallback Behavior
Each route includes intelligent fallback:
- **Azure routes**: Use `get_message_descriptions` method
- **Astra routes**: Try service methods first, fall back to legacy `astrapy_handler` functions if needed

**Note**: Routes now support dynamic switching! Change your `DATABASE_PROVIDER` environment variable and the next request will use the new provider without requiring an application restart.

## Backwards Compatibility

All existing code continues to work without changes:

```python
# This still works regardless of the underlying provider
from astrapy_handler import get_policy_query, writeBlog

result = get_policy_query("environmental policy")
blog = writeBlog("sustainability practices")
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```
   ImportError: azure.search.documents
   ```
   Solution: Install Azure dependencies with `pip install -r requirements-azure.txt`

2. **Configuration Errors**
   ```
   ValueError: Missing required configuration for azure: AZURE_SEARCH_ENDPOINT
   ```
   Solution: Set the required environment variables for your chosen provider

3. **Index Not Found**
   ```
   Error getting policy assertions from Azure: index 'assertions' not found
   ```
   Solution: Create the required indexes in your Azure Search service

### Health Checks

Use the health check feature to verify your database connection:

```python
from database_service import database_service

if database_service.health_check():
    print("✅ Database connection is healthy")
else:
    print("❌ Database connection failed")
```

## Performance Considerations

- **Astra DB**: Optimized for vector similarity search, native vector support
- **Azure Search**: General-purpose search with vector capabilities, may require tuning

Choose the provider that best fits your performance and cost requirements.

## Support

For provider-specific issues:
- **Astra DB**: Check DataStax documentation
- **Azure Search**: Check Microsoft Azure documentation
- **Application Issues**: Check the application logs for detailed error messages
