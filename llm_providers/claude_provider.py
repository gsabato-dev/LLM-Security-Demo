"""
Anthropic Claude LLM Provider.
"""
from anthropic import Anthropic
from typing import List, Dict, Optional, Callable
from .base_provider import BaseLLMProvider


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude implementation."""

    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022", prompt_version: str = "strict"):
        super().__init__(api_key, model_name, prompt_version)
        self.client = Anthropic(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "Anthropic Claude"

    def get_available_models(self) -> List[str]:
        """Return list of available Claude models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]

    def check_connection(self) -> bool:
        """Verify API key works."""
        try:
            # Try a minimal API call to check connection
            self.client.messages.create(
                model=self.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception as e:
            print(f"Claude connection error: {e}")
            return False

    def send_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Send a message to Claude."""
        try:
            # Build messages array
            messages = []

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": message})

            # Send to Claude
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                system=self.system_prompt,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"

    def send_message_with_tools(
        self,
        message: str,
        tools: List[Dict],
        conversation_history: List[Dict[str, str]] = None,
        tool_handler: Callable = None
    ) -> str:
        """Send a message with function calling."""
        try:
            # Build messages array
            messages = []

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": message})

            # Convert tools to Claude format
            claude_tools = []
            for tool in tools:
                claude_tools.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": {
                        "type": "object",
                        "properties": tool.get("parameters", {}),
                        "required": tool.get("required", [])
                    }
                })

            # Send to Claude with tools
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                system=self.system_prompt,
                messages=messages,
                tools=claude_tools
            )

            # Handle tool calls
            while response.stop_reason == "tool_use":
                # Find tool use in response
                tool_use = None
                for block in response.content:
                    if block.type == "tool_use":
                        tool_use = block
                        break

                if tool_use:
                    function_name = tool_use.name
                    function_args = tool_use.input

                    # Execute the function
                    if tool_handler:
                        function_result = tool_handler(function_name, function_args)
                    else:
                        function_result = {"error": "No tool handler provided"}

                    # Add assistant's response to messages
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    # Add tool result to messages
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": str(function_result)
                            }
                        ]
                    })

                    # Get next response
                    response = self.client.messages.create(
                        model=self.model_name,
                        max_tokens=2048,
                        system=self.system_prompt,
                        messages=messages,
                        tools=claude_tools
                    )
                else:
                    break

            # Extract final text response
            for block in response.content:
                if hasattr(block, 'text'):
                    return block.text

            return "No text response from Claude"

        except Exception as e:
            return f"Error with Claude function calling: {str(e)}"
