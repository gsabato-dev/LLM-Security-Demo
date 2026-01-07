"""
Configuration manager for LLM Prompt Injection Testing App.
Supports both .env file and Google Secret Manager.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration manager with support for .env and Google Secret Manager."""

    def __init__(self):
        self.use_secret_manager = os.getenv("USE_SECRET_MANAGER", "false").lower() == "true"
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID")

        # Initialize Secret Manager client if needed
        self._secret_client = None
        if self.use_secret_manager:
            try:
                from google.cloud import secretmanager
                self._secret_client = secretmanager.SecretManagerServiceClient()
            except ImportError:
                print("Warning: google-cloud-secret-manager not installed. Falling back to .env")
                self.use_secret_manager = False

    def _get_from_secret_manager(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from Google Secret Manager."""
        if not self._secret_client or not self.gcp_project_id:
            return None

        try:
            name = f"projects/{self.gcp_project_id}/secrets/{secret_name}/versions/latest"
            response = self._secret_client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            print(f"Error retrieving secret {secret_name}: {e}")
            return None

    def get_secret(self, env_var_name: str, secret_name: str = None) -> Optional[str]:
        """
        Get secret from Secret Manager or .env file.

        Args:
            env_var_name: Environment variable name (e.g., "GEMINI_API_KEY")
            secret_name: Secret Manager secret name (defaults to env_var_name in lowercase with hyphens)

        Returns:
            The secret value or None if not found
        """
        # Try Secret Manager first if enabled
        if self.use_secret_manager:
            if secret_name is None:
                # Convert GEMINI_API_KEY to gemini-api-key
                secret_name = env_var_name.lower().replace("_", "-")

            value = self._get_from_secret_manager(secret_name)
            if value:
                return value

        # Fall back to environment variable
        return os.getenv(env_var_name)

    # API Keys
    @property
    def gemini_api_key(self) -> Optional[str]:
        return self.get_secret("GEMINI_API_KEY")

    @property
    def openai_api_key(self) -> Optional[str]:
        return self.get_secret("OPENAI_API_KEY")

    @property
    def anthropic_api_key(self) -> Optional[str]:
        return self.get_secret("ANTHROPIC_API_KEY")

    # GCP settings for Vertex AI
    @property
    def gcp_location(self) -> str:
        """Get GCP location for Vertex AI."""
        return os.getenv("GCP_LOCATION", "us-central1")

    # App settings
    @property
    def default_provider(self) -> str:
        return os.getenv("DEFAULT_PROVIDER", "gemini")

    @property
    def database_path(self) -> str:
        return os.getenv("DATABASE_PATH", "recipes.db")

    @property
    def enable_logging(self) -> bool:
        return os.getenv("ENABLE_LOGGING", "true").lower() == "true"

    @property
    def log_file(self) -> str:
        return os.getenv("LOG_FILE", "injection_attempts.log")

    @property
    def prompt_version(self) -> str:
        """Get the prompt version to use (strict, moderate, relaxed, minimal, none)."""
        return os.getenv("PROMPT_VERSION", "strict")


# Global config instance
config = Config()
