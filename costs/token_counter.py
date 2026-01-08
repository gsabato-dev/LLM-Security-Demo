"""
Token Counter Utility

Estimates token counts for different LLM providers.
"""

import re
from typing import Optional


class TokenCounter:
    """Estimates token counts for text."""

    def __init__(self):
        """Initialize token counter."""
        self.tiktoken_available = False
        self.tiktoken_encoding = None

        # Try to import tiktoken for OpenAI models
        try:
            import tiktoken
            self.tiktoken_encoding = tiktoken.get_encoding("cl100k_base")
            self.tiktoken_available = True
        except ImportError:
            pass

    def count_tokens(self, text: str, model_name: str = None) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens in
            model_name: Optional model name for better accuracy

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        # Use tiktoken if available (most accurate for OpenAI/similar models)
        if self.tiktoken_available and self.tiktoken_encoding:
            try:
                return len(self.tiktoken_encoding.encode(text))
            except Exception:
                pass

        # Fallback: approximation based on characters
        # Different models have different tokenization, but this is a reasonable estimate
        # Average: ~4 characters per token for English text
        # More conservative: ~3.5 characters per token (accounts for special tokens, punctuation)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Rough estimate: 1 token ≈ 3.5 characters on average
        # Add 10% buffer for safety
        estimated_tokens = int((len(text) / 3.5) * 1.1)

        return max(1, estimated_tokens)  # At least 1 token

    def count_messages_tokens(self, messages: list, model_name: str = None) -> int:
        """
        Count tokens in a list of messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model_name: Optional model name

        Returns:
            Estimated token count
        """
        total = 0

        for message in messages:
            # Count message content
            if isinstance(message, dict) and 'content' in message:
                total += self.count_tokens(message['content'], model_name)

                # Add overhead for message formatting (~4 tokens per message)
                total += 4

        return total

    def estimate_response_tokens(self, prompt_tokens: int, average_response_ratio: float = 2.0) -> int:
        """
        Estimate response tokens based on prompt.

        Args:
            prompt_tokens: Number of tokens in prompt
            average_response_ratio: Ratio of response to prompt (default 2.0)

        Returns:
            Estimated response tokens
        """
        # For our recipe chatbot, responses are typically similar length to prompts
        # or slightly longer. Use conservative estimate.
        return int(prompt_tokens * average_response_ratio)

    def count_tool_tokens(self, tools: list) -> int:
        """
        Count tokens in tool definitions.

        Args:
            tools: List of tool/function definitions

        Returns:
            Estimated token count
        """
        import json

        total = 0
        for tool in tools:
            # Convert tool to string and count
            tool_str = json.dumps(tool, separators=(',', ':'))
            total += self.count_tokens(tool_str)

        return total


# Global instance
_counter = None


def get_token_counter() -> TokenCounter:
    """Get global token counter instance."""
    global _counter
    if _counter is None:
        _counter = TokenCounter()
    return _counter


def count_tokens(text: str, model_name: str = None) -> int:
    """
    Count tokens in text (convenience function).

    Args:
        text: Text to count
        model_name: Optional model name

    Returns:
        Token count
    """
    return get_token_counter().count_tokens(text, model_name)


def estimate_test_suite_cost(num_tests: int, model_name: str,
                             avg_prompt_tokens: int = 150,
                             avg_response_tokens: int = 300) -> dict:
    """
    Estimate cost for running test suite.

    Args:
        num_tests: Number of tests to run
        model_name: Model name
        avg_prompt_tokens: Average tokens per prompt (default ~150)
        avg_response_tokens: Average tokens per response (default ~300)

    Returns:
        Cost estimate dict
    """
    from .pricing_config import estimate_cost

    # Account for tool definitions (sent with each request)
    tool_tokens = 400  # Approximate tokens for 4 tool definitions

    total_input_tokens = num_tests * (avg_prompt_tokens + tool_tokens)
    total_output_tokens = num_tests * avg_response_tokens

    return estimate_cost(total_input_tokens, total_output_tokens, model_name)
