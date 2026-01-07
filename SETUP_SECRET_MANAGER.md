# Google Cloud Secret Manager Setup Guide

Complete guide for setting up Google Cloud Secret Manager for the LLM Injection Testing App.

## Why Use Secret Manager?

- **Security**: API keys never stored in files or code
- **Centralized**: Manage all secrets in one place
- **Audit**: Track who accessed secrets and when
- **Rotation**: Easy to update secrets without changing code
- **Sharing**: Share app publicly without exposing keys

## Prerequisites

- Google Cloud account (free tier available)
- gcloud CLI installed ([download here](https://cloud.google.com/sdk/docs/install))
- Billing enabled (Secret Manager requires billing, but has free tier)

## Complete Setup Steps

### 1. Install gcloud CLI (if needed)

**macOS:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Or use Homebrew:**
```bash
brew install google-cloud-sdk
```

**Initialize:**
```bash
gcloud init
```

### 2. Authenticate

```bash
# Login to your Google account
gcloud auth login

# Set up application default credentials (for local dev)
gcloud auth application-default login
```

### 3. Create or Select Project

**List existing projects:**
```bash
gcloud projects list
```

**Create new project (recommended):**
```bash
# Create project
gcloud projects create llm-injection-test \
    --name="LLM Injection Tester" \
    --set-as-default

# Or use your own project ID
gcloud projects create YOUR_PROJECT_ID \
    --name="Your Project Name" \
    --set-as-default
```

**Or select existing project:**
```bash
gcloud config set project YOUR_EXISTING_PROJECT_ID
```

**Get your project ID:**
```bash
gcloud config get-value project
# Save this - you'll need it for .env file
```

### 4. Enable Billing

Secret Manager requires a billing account (free tier available):

```bash
# List billing accounts
gcloud billing accounts list

# Link billing to project (if needed)
gcloud billing projects link YOUR_PROJECT_ID \
    --billing-account=BILLING_ACCOUNT_ID
```

Or enable via Cloud Console: https://console.cloud.google.com/billing

**Free Tier**: 6 active secret versions, 10,000 accesses/month (plenty for this app!)

### 5. Enable Required APIs

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Verify it's enabled
gcloud services list --enabled | grep secretmanager
```

### 6. Create Secrets

**Create Gemini API key secret:**
```bash
# Replace with your actual API key
echo -n "YOUR_ACTUAL_GEMINI_API_KEY" | \
    gcloud secrets create gemini-api-key \
    --data-file=- \
    --replication-policy="automatic"
```

**Optional - Create OpenAI secret:**
```bash
echo -n "YOUR_ACTUAL_OPENAI_API_KEY" | \
    gcloud secrets create openai-api-key \
    --data-file=- \
    --replication-policy="automatic"
```

**Optional - Create Anthropic secret:**
```bash
echo -n "YOUR_ACTUAL_ANTHROPIC_API_KEY" | \
    gcloud secrets create anthropic-api-key \
    --data-file=- \
    --replication-policy="automatic"
```

**Verify secrets:**
```bash
gcloud secrets list

# View secret metadata (not the value)
gcloud secrets describe gemini-api-key
```

### 7. Set Permissions

**For local development**, Application Default Credentials automatically work if you're logged in.

**For production or service accounts:**

```bash
# Create service account
gcloud iam service-accounts create llm-injection-app \
    --display-name="LLM Injection Test App"

# Grant Secret Manager access
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
    --member="serviceAccount:llm-injection-app@$(gcloud config get-value project).iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create and download key
gcloud iam service-accounts keys create ~/llm-injection-service-account.json \
    --iam-account=llm-injection-app@$(gcloud config get-value project).iam.gserviceaccount.com

# Export the path
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/llm-injection-service-account.json"

# Add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/llm-injection-service-account.json"' >> ~/.zshrc
```

### 8. Configure the App

Create your `.env` file:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Enable Secret Manager
USE_SECRET_MANAGER=true

# Your GCP Project ID (from step 3)
GCP_PROJECT_ID=llm-injection-test

# Everything else can be commented out or removed
# API keys are now in GCP Secret Manager
# GEMINI_API_KEY=
# OPENAI_API_KEY=
# ANTHROPIC_API_KEY=

# Optional settings
DEFAULT_PROVIDER=gemini
DATABASE_PATH=recipes.db
ENABLE_LOGGING=true
```

### 9. Test the Setup

Run the test script:
```bash
source venv/bin/activate
python test_secret_manager.py
```

Expected output:
```
🔍 Testing Google Cloud Secret Manager Setup

USE_SECRET_MANAGER: True
GCP_PROJECT_ID: llm-injection-test

📥 Testing secret retrieval...

✅ Gemini API Key: AIzaSyBr...xyz123
✅ OpenAI API Key: sk-proj-...abc456
✅ Anthropic API Key: sk-ant-...def789

📊 Result: 3/3 secrets retrieved

🎉 All secrets retrieved successfully!
Your Secret Manager setup is working perfectly!
```

### 10. Run the App

```bash
streamlit run app.py
```

## Managing Secrets

### Update a Secret Value

```bash
# Add a new version
echo -n "NEW_API_KEY_VALUE" | \
    gcloud secrets versions add gemini-api-key --data-file=-

# The app automatically uses the latest version
```

### View Secret Versions

```bash
# List all versions
gcloud secrets versions list gemini-api-key

# Access a specific version (for rollback)
gcloud secrets versions access 1 --secret=gemini-api-key
```

### Delete a Secret

```bash
# Delete the entire secret
gcloud secrets delete gemini-api-key

# Or disable a specific version
gcloud secrets versions disable 1 --secret=gemini-api-key
```

### View Audit Logs

```bash
# See who accessed secrets (requires logging enabled)
gcloud logging read "resource.type=secret_manager" --limit=10
```

## Troubleshooting

### Error: "Permission denied"

```bash
# Check your authentication
gcloud auth list

# Re-authenticate
gcloud auth application-default login

# Verify project
gcloud config get-value project
```

### Error: "Secret not found"

```bash
# List secrets to verify name
gcloud secrets list

# Check secret exists in correct project
gcloud config get-value project
gcloud secrets describe gemini-api-key
```

### Error: "API not enabled"

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Wait a few minutes and try again
```

### Error: "Billing account required"

- Go to: https://console.cloud.google.com/billing
- Link a billing account to your project
- Free tier covers typical usage for this app

### Python Import Error

```bash
# Install the Secret Manager library
pip install google-cloud-secret-manager

# Or reinstall all requirements
pip install -r requirements.txt
```

### Test script shows "Not found"

```bash
# Verify secrets exist
gcloud secrets list

# Check secret naming (must match exactly)
# App expects: gemini-api-key, openai-api-key, anthropic-api-key

# Verify you have access
gcloud secrets versions access latest --secret=gemini-api-key
```

## Cost Breakdown

**Free Tier (Monthly):**
- 6 active secret versions: FREE
- 10,000 access operations: FREE

**Beyond Free Tier:**
- $0.06 per active secret version per month
- $0.03 per 10,000 access operations

**For this app**: You'll stay in free tier unless you create many secrets or have extremely high traffic.

## Security Best Practices

1. **Never commit secrets to git** - they're in GCP now!
2. **Use least privilege** - only grant secretAccessor role
3. **Enable audit logging** - track secret access
4. **Rotate secrets regularly** - use version management
5. **Use service accounts in production** - not user credentials
6. **Delete old versions** - reduce attack surface

## Sharing Your App

When sharing this app publicly:

1. ✅ `.gitignore` already excludes `.env` and `credentials.json`
2. ✅ Users create their own secrets in their GCP project
3. ✅ Each user's secrets are isolated
4. ✅ No shared credentials

Users can choose:
- **Simple**: Use `.env` file (copy `.env.example`)
- **Advanced**: Set up their own Secret Manager

## Alternative: Mix Both Methods

You can use Secret Manager for some keys and `.env` for others:

```bash
# .env file
USE_SECRET_MANAGER=true
GCP_PROJECT_ID=your-project

# Gemini from Secret Manager (not in .env)
# OpenAI from .env file
OPENAI_API_KEY=sk-your-key

# Anthropic from .env file
ANTHROPIC_API_KEY=sk-ant-your-key
```

The app will:
1. Try Secret Manager first
2. Fall back to `.env` if not found
3. Work seamlessly with mixed configuration

## Quick Reference

```bash
# Create secret
echo -n "value" | gcloud secrets create NAME --data-file=-

# Update secret
echo -n "new_value" | gcloud secrets versions add NAME --data-file=-

# List secrets
gcloud secrets list

# Read secret value
gcloud secrets versions access latest --secret=NAME

# Delete secret
gcloud secrets delete NAME

# Test setup
python test_secret_manager.py
```

## Getting Help

- [Secret Manager Docs](https://cloud.google.com/secret-manager/docs)
- [Free Tier Details](https://cloud.google.com/secret-manager/pricing)
- [Security Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)
- [Quickstart Guide](https://cloud.google.com/secret-manager/docs/quickstart)

## Next Steps

1. Complete setup above
2. Run `python test_secret_manager.py`
3. If successful, run `streamlit run app.py`
4. Start testing prompt injections! 🔐
