"""
Base LLM Provider interface.
All LLM providers must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Callable
from prompt_versions import get_prompt_version


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, model_name: str = None, prompt_version: str = "strict"):
        """
        Initialize the provider.

        Args:
            api_key: API key for the provider
            model_name: Specific model to use (optional)
            prompt_version: Security level of system prompt (strict, moderate, relaxed, minimal, none)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.prompt_version = prompt_version
        self.system_prompt = get_prompt_version(prompt_version)

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models for this provider."""
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """
        Verify API key is valid and connection works.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def send_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Send a message and get response.

        Args:
            message: User message
            conversation_history: Previous messages [{"role": "user/assistant", "content": "..."}]

        Returns:
            Assistant's response
        """
        pass

    @abstractmethod
    def send_message_with_tools(
        self,
        message: str,
        tools: List[Dict],
        conversation_history: List[Dict[str, str]] = None,
        tool_handler: Callable = None
    ) -> str:
        """
        Send a message with tool/function calling capabilities.

        Args:
            message: User message
            tools: List of tool definitions
            conversation_history: Previous messages
            tool_handler: Function to execute tools

        Returns:
            Assistant's response after tool execution
        """
        pass


    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass
