"""
Unified LLM client interface.
Provides a simple way to create and use LLM providers across apps.
"""
from typing import Dict, Any, Optional, Callable, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_providers import LLMProviderFactory, BaseLLMProvider
from llm_injection.prompt_versions import (
    get_prompt_version,
    list_prompt_versions,
    get_version_info,
    PROMPT_VERSIONS
)
from llm_injection.config import config


class LLMClient:
    """
    Unified LLM client that wraps provider creation and message handling.
    """

    def __init__(
        self,
        provider_name: str = None,
        model_name: str = None,
        prompt_version: str = "strict",
        custom_prompt: str = None
    ):
        """
        Initialize LLM client.

        Args:
            provider_name: Provider to use (gemini, openai, claude, vertex_ai)
            model_name: Specific model name (uses provider default if None)
            prompt_version: Security level (strict, moderate, relaxed, none)
            custom_prompt: Override system prompt entirely
        """
        self.provider_name = provider_name or config.default_provider
        self.model_name = model_name
        self.prompt_version = prompt_version
        self.custom_prompt = custom_prompt
        self._provider: Optional[BaseLLMProvider] = None

    @property
    def provider(self) -> BaseLLMProvider:
        """Get or create the LLM provider."""
        if self._provider is None:
            self._provider = self._create_provider()
        return self._provider

    def _create_provider(self) -> BaseLLMProvider:
        """Create the underlying LLM provider."""
        provider_name = self.provider_name

        # Get appropriate API key or credentials
        if provider_name == "vertex_ai":
            provider = LLMProviderFactory.create_provider(
                provider_name=provider_name,
                model_name=self.model_name,
                project_id=config.gcp_project_id,
                location=config.gcp_location,
                prompt_version=self.prompt_version
            )
        else:
            # Get API key based on provider
            if provider_name == "gemini":
                api_key = config.gemini_api_key
            elif provider_name == "openai":
                api_key = config.openai_api_key
            elif provider_name == "claude":
                api_key = config.anthropic_api_key
            else:
                raise ValueError(f"Unknown provider: {provider_name}")

            if not api_key:
                raise ValueError(f"No API key configured for {provider_name}")

            provider = LLMProviderFactory.create_provider(
                provider_name=provider_name,
                api_key=api_key,
                model_name=self.model_name,
                prompt_version=self.prompt_version
            )

        # Override system prompt if custom provided
        if self.custom_prompt:
            provider.system_prompt = self.custom_prompt
            # For Vertex AI, need to recreate the model
            if provider_name == "vertex_ai":
                from vertexai.generative_models import GenerativeModel
                provider.model = GenerativeModel(
                    model_name=provider.model_name,
                    system_instruction=[self.custom_prompt]
                )

        return provider

    def reset(self):
        """Reset the provider (forces recreation on next use)."""
        self._provider = None

    def set_prompt_version(self, version: str):
        """Change the prompt version and reset provider."""
        self.prompt_version = version
        self.custom_prompt = None
        self.reset()

    def set_custom_prompt(self, prompt: str):
        """Set a custom prompt and reset provider."""
        self.custom_prompt = prompt
        self.reset()

    def send_message(
        self,
        message: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Send a simple message (no tools).

        Args:
            message: User message
            conversation_history: Previous messages

        Returns:
            Assistant response text
        """
        return self.provider.send_message(
            message=message,
            conversation_history=conversation_history or []
        )

    def send_message_with_tools(
        self,
        message: str,
        tools: List[Dict],
        tool_handler: Callable[[str, Dict[str, Any]], Dict],
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Send a message with tool support.

        Args:
            message: User message
            tools: List of tool definitions
            tool_handler: Function to handle tool calls
            conversation_history: Previous messages

        Returns:
            Assistant response text
        """
        return self.provider.send_message_with_tools(
            message=message,
            tools=tools,
            conversation_history=conversation_history or [],
            tool_handler=tool_handler
        )

    @property
    def system_prompt(self) -> str:
        """Get current system prompt."""
        if self.custom_prompt:
            return self.custom_prompt
        return get_prompt_version(self.prompt_version)

    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available provider names."""
        return LLMProviderFactory.get_available_providers()

    @staticmethod
    def get_prompt_versions() -> List[tuple]:
        """Get list of available prompt versions."""
        return list_prompt_versions()

    @staticmethod
    def get_prompt_info(version: str) -> Dict:
        """Get info about a prompt version."""
        return get_version_info(version)


def create_client(
    provider: str = None,
    model: str = None,
    security_level: str = "strict"
) -> LLMClient:
    """
    Convenience function to create an LLM client.

    Args:
        provider: Provider name (uses config default if None)
        model: Model name (uses provider default if None)
        security_level: Prompt security level

    Returns:
        Configured LLMClient instance
    """
    return LLMClient(
        provider_name=provider,
        model_name=model,
        prompt_version=security_level
    )
