#!/bin/bash
# Quick setup script for Google Cloud Secret Manager
# This automates the Secret Manager setup process

set -e  # Exit on error

echo "🔐 Google Cloud Secret Manager Setup"
echo "===================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found!"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
echo "Current GCP project: ${CURRENT_PROJECT:-none}"
echo ""

# Ask for project ID
read -p "Enter GCP Project ID (or press Enter to create new): " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    # Create new project
    echo ""
    read -p "Enter new project ID (e.g., llm-injection-test): " NEW_PROJECT_ID
    read -p "Enter project name (e.g., LLM Injection Tester): " PROJECT_NAME

    echo "Creating project $NEW_PROJECT_ID..."
    gcloud projects create "$NEW_PROJECT_ID" --name="$PROJECT_NAME"
    PROJECT_ID="$NEW_PROJECT_ID"
fi

# Set project
echo "Setting project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

echo ""
echo "✅ Project set to: $PROJECT_ID"
echo ""

# Enable Secret Manager API
echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

echo ""
echo "✅ Secret Manager API enabled"
echo ""

# Create secrets
echo "Now let's create your API key secrets"
echo "======================================"
echo ""

# Gemini API Key
read -p "Do you want to create Gemini API key secret? (y/n): " CREATE_GEMINI
if [ "$CREATE_GEMINI" = "y" ]; then
    echo "Get your Gemini API key from: https://makersuite.google.com/app/apikey"
    read -sp "Enter Gemini API key: " GEMINI_KEY
    echo ""

    if [ -n "$GEMINI_KEY" ]; then
        echo "$GEMINI_KEY" | gcloud secrets create gemini-api-key \
            --data-file=- \
            --replication-policy="automatic" 2>/dev/null || \
            echo "$GEMINI_KEY" | gcloud secrets versions add gemini-api-key --data-file=-
        echo "✅ Gemini API key secret created/updated"
    fi
fi

echo ""

# OpenAI API Key
read -p "Do you want to create OpenAI API key secret? (y/n): " CREATE_OPENAI
if [ "$CREATE_OPENAI" = "y" ]; then
    echo "Get your OpenAI API key from: https://platform.openai.com/api-keys"
    read -sp "Enter OpenAI API key: " OPENAI_KEY
    echo ""

    if [ -n "$OPENAI_KEY" ]; then
        echo "$OPENAI_KEY" | gcloud secrets create openai-api-key \
            --data-file=- \
            --replication-policy="automatic" 2>/dev/null || \
            echo "$OPENAI_KEY" | gcloud secrets versions add openai-api-key --data-file=-
        echo "✅ OpenAI API key secret created/updated"
    fi
fi

echo ""

# Anthropic API Key
read -p "Do you want to create Anthropic API key secret? (y/n): " CREATE_ANTHROPIC
if [ "$CREATE_ANTHROPIC" = "y" ]; then
    echo "Get your Anthropic API key from: https://console.anthropic.com/"
    read -sp "Enter Anthropic API key: " ANTHROPIC_KEY
    echo ""

    if [ -n "$ANTHROPIC_KEY" ]; then
        echo "$ANTHROPIC_KEY" | gcloud secrets create anthropic-api-key \
            --data-file=- \
            --replication-policy="automatic" 2>/dev/null || \
            echo "$ANTHROPIC_KEY" | gcloud secrets versions add anthropic-api-key --data-file=-
        echo "✅ Anthropic API key secret created/updated"
    fi
fi

echo ""
echo "======================================"
echo "Secrets created! Here's what you have:"
echo "======================================"
gcloud secrets list

echo ""
echo "======================================"
echo "Setting up authentication..."
echo "======================================"

# Set up application default credentials
echo "Configuring application default credentials..."
gcloud auth application-default login

echo ""
echo "======================================"
echo "Updating .env file..."
echo "======================================"

# Update .env file
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    cp .env.example "$ENV_FILE"
fi

# Update or add configuration
if grep -q "USE_SECRET_MANAGER" "$ENV_FILE"; then
    sed -i.bak "s/USE_SECRET_MANAGER=.*/USE_SECRET_MANAGER=true/" "$ENV_FILE"
else
    echo "USE_SECRET_MANAGER=true" >> "$ENV_FILE"
fi

if grep -q "GCP_PROJECT_ID" "$ENV_FILE"; then
    sed -i.bak "s/GCP_PROJECT_ID=.*/GCP_PROJECT_ID=$PROJECT_ID/" "$ENV_FILE"
else
    echo "GCP_PROJECT_ID=$PROJECT_ID" >> "$ENV_FILE"
fi

echo "✅ .env file updated"

echo ""
echo "======================================"
echo "🎉 Setup Complete!"
echo "======================================"
echo ""
echo "Your secrets are now stored in Google Cloud Secret Manager!"
echo ""
echo "Next steps:"
echo "1. Run the app:"
echo "   streamlit run apps/red_blue_team_app.py"
echo ""
echo "To manage your secrets:"
echo "- List secrets: gcloud secrets list"
echo "- Update secret: echo -n 'new_key' | gcloud secrets versions add SECRET_NAME --data-file=-"
echo "- View secret: gcloud secrets versions access latest --secret=SECRET_NAME"
echo ""
echo "For more details, see: SETUP_SECRET_MANAGER.md"
