#!/usr/bin/env python3
"""
Example script demonstrating database provider switching.
Run this script to test switching between Astra DB and Azure Search.
"""

import os
import sys
from database_service import DatabaseService
from config import config

def main():
    """Main function to demonstrate database switching."""
    print("🚀 Database Provider Switching Demo")
    print("=" * 50)
    
    # Show current configuration
    print(f"📋 Current DATABASE_PROVIDER: {config.database_provider}")
    print(f"🔑 OpenAI API Key configured: {'✅' if config.openai_api_key else '❌'}")
    
    # Test configuration validation
    try:
        config.validate_config()
        print("✅ Configuration validation passed")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Tip: Make sure to set the required environment variables for your chosen provider")
        return 1
    
    # Create database service
    try:
        db_service = DatabaseService()
        print(f"🗄️  Database service initialized with: {db_service.get_current_provider()}")
    except Exception as e:
        print(f"❌ Failed to initialize database service: {e}")
        return 1
    
    # Perform health check
    print("\n🏥 Performing health check...")
    if db_service.health_check():
        print("✅ Database connection is healthy")
    else:
        print("❌ Database health check failed")
        return 1
    
    # Test a simple query
    print("\n🔍 Testing a simple query...")
    try:
        results = db_service.get_policy_assertions("environmental policy", limit=2)
        print(f"✅ Query successful! Retrieved {len(results)} results")
        
        if results:
            print("📄 Sample result:")
            result = results[0]
            for key, value in list(result.items())[:3]:  # Show first 3 fields
                print(f"   {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return 1
    
    # Demonstrate switching (if multiple providers are configured)
    print("\n🔄 Testing provider switching...")
    current_provider = config.database_provider
    
    # Try to switch to the other provider
    other_provider = "azure" if current_provider == "astra" else "astra"
    
    print(f"💭 Attempting to switch from {current_provider} to {other_provider}...")
    
    # Check if the other provider is configured
    if other_provider == "azure":
        if not config.azure_search_endpoint or not config.azure_search_key:
            print("⚠️  Azure Search not configured - skipping switch test")
            print("   Set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY to test switching")
        else:
            try:
                db_service.switch_provider("azure")
                print(f"✅ Successfully switched to: {db_service.get_current_provider()}")
                
                # Test health check with new provider
                if db_service.health_check():
                    print("✅ New provider health check passed")
                else:
                    print("❌ New provider health check failed")
            except Exception as e:
                print(f"❌ Failed to switch to Azure: {e}")
    
    elif other_provider == "astra":
        if not config.astra_token:
            print("⚠️  Astra DB not configured - skipping switch test")
            print("   Set ASTRADB_TOKEN to test switching")
        else:
            try:
                db_service.switch_provider("astra")
                print(f"✅ Successfully switched to: {db_service.get_current_provider()}")
                
                # Test health check with new provider
                if db_service.health_check():
                    print("✅ New provider health check passed")
                else:
                    print("❌ New provider health check failed")
            except Exception as e:
                print(f"❌ Failed to switch to Astra: {e}")
    
    print("\n🎉 Demo completed successfully!")
    print("\n📚 For more information, see DATABASE_SWITCHING_GUIDE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
