"""
LLM Provider Factory.
Creates the appropriate provider based on configuration.
"""
from typing import Optional
from .base_provider import BaseLLMProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .vertex_ai_provider import VertexAIProvider


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    PROVIDERS = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "vertex_ai": VertexAIProvider
    }

    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        api_key: str = None,
        model_name: Optional[str] = None,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        prompt_version: str = "strict"
    ) -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_name: Name of the provider (gemini, openai, claude, vertex_ai)
            api_key: API key for the provider (not needed for vertex_ai)
            model_name: Optional specific model name
            project_id: GCP project ID (for vertex_ai)
            location: GCP location (for vertex_ai)
            prompt_version: Security level of system prompt (strict, moderate, relaxed, minimal, none)

        Returns:
            LLMProvider instance

        Raises:
            ValueError: If provider_name is not supported
        """
        provider_name = provider_name.lower()

        if provider_name not in cls.PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {', '.join(cls.PROVIDERS.keys())}"
            )

        provider_class = cls.PROVIDERS[provider_name]

        # Use default model if not specified
        if model_name is None:
            if provider_name == "gemini":
                model_name = "gemini-2.0-flash"
            elif provider_name == "openai":
                model_name = "gpt-4"
            elif provider_name == "claude":
                model_name = "claude-3-5-sonnet-20241022"
            elif provider_name == "vertex_ai":
                model_name = "gemini-2.0-flash-001"

        # Handle Vertex AI with different parameters
        if provider_name == "vertex_ai":
            return provider_class(
                model_name=model_name,
                project_id=project_id,
                location=location or "us-central1",
                prompt_version=prompt_version
            )
        else:
            return provider_class(api_key=api_key, model_name=model_name, prompt_version=prompt_version)

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names."""
        return list(cls.PROVIDERS.keys())


__all__ = [
    "BaseLLMProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "ClaudeProvider",
    "VertexAIProvider",
    "LLMProviderFactory"
]
