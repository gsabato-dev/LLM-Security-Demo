"""
Shared modules for LLM Security Demo apps.
Provides unified access to database, security utilities, and LLM client.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Re-export database
from llm_injection.database import RecipeDatabase, db

# Re-export config
from llm_injection.config import Config, config

# Re-export prompt versions
from llm_injection.prompt_versions import (
    PROMPT_VERSIONS,
    get_prompt_version,
    list_prompt_versions,
    get_version_info
)

# Re-export logger (for apps that need stateful tracking)
from llm_injection.logger import InjectionLogger, logger

# Export security utilities
from .security import (
    # Leak detection
    check_secret_leak,
    check_pii_leak,
    check_prompt_leak,
    build_secrets_list,
    build_pii_list,
    extract_keywords,
    extract_pii_keywords,
    # LLM05: HTML sanitization
    sanitize_html,
    check_html_safety,
    # LLM05: Action validation
    validate_action_json,
    ALLOWED_ACTIONS,
    FORBIDDEN_ACTIONS,
)

# Export LLM client
from .llm_client import LLMClient, create_client

__all__ = [
    # Database
    "RecipeDatabase",
    "db",
    # Config
    "Config",
    "config",
    # Prompts
    "PROMPT_VERSIONS",
    "get_prompt_version",
    "list_prompt_versions",
    "get_version_info",
    # Logger
    "InjectionLogger",
    "logger",
    # Security utilities
    "check_secret_leak",
    "check_pii_leak",
    "check_prompt_leak",
    "build_secrets_list",
    "build_pii_list",
    "extract_keywords",
    "extract_pii_keywords",
    "sanitize_html",
    "check_html_safety",
    "validate_action_json",
    "ALLOWED_ACTIONS",
    "FORBIDDEN_ACTIONS",
    # LLM Client
    "LLMClient",
    "create_client",
]
