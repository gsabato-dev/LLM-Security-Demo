#!/usr/bin/env python3
"""
Test script for Google Cloud Secret Manager setup.
Run this to verify your Secret Manager configuration works.
"""
from config import config

def test_secret_manager():
    """Test Secret Manager access."""
    print("🔍 Testing Google Cloud Secret Manager Setup\n")

    # Check configuration
    print(f"USE_SECRET_MANAGER: {config.use_secret_manager}")
    print(f"GCP_PROJECT_ID: {config.gcp_project_id}\n")

    if not config.use_secret_manager:
        print("⚠️  Secret Manager is disabled in .env")
        print("Set USE_SECRET_MANAGER=true to enable\n")
        return

    if not config.gcp_project_id:
        print("❌ GCP_PROJECT_ID not set in .env")
        print("Add your GCP project ID to .env\n")
        return

    # Test retrieving secrets
    print("📥 Testing secret retrieval...\n")

    secrets_to_test = [
        ("Gemini API Key", "gemini-api-key", config.gemini_api_key),
        ("OpenAI API Key", "openai-api-key", config.openai_api_key),
        ("Anthropic API Key", "anthropic-api-key", config.anthropic_api_key)
    ]

    success_count = 0
    for name, secret_name, value in secrets_to_test:
        if value:
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {name}: {masked_value}")
            success_count += 1
        else:
            print(f"⚠️  {name}: Not found (secret: {secret_name})")

    print(f"\n📊 Result: {success_count}/{len(secrets_to_test)} secrets retrieved")

    if success_count == 0:
        print("\n❌ No secrets could be retrieved. Check:")
        print("   1. gcloud auth application-default login")
        print("   2. Secrets exist: gcloud secrets list")
        print("   3. You have secretmanager.secretAccessor role")
    elif success_count == len(secrets_to_test):
        print("\n🎉 All secrets retrieved successfully!")
        print("Your Secret Manager setup is working perfectly!")
    else:
        print("\n⚠️  Some secrets are missing.")
        print("Create missing secrets with:")
        print('   echo -n "your_api_key" | gcloud secrets create SECRET_NAME --data-file=-')

if __name__ == "__main__":
    test_secret_manager()
