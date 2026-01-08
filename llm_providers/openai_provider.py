"""
OpenAI LLM Provider.
"""
import json
from openai import OpenAI
from typing import List, Dict, Optional, Callable
from .base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI implementation."""

    def __init__(self, api_key: str, model_name: str = "gpt-4", prompt_version: str = "strict"):
        super().__init__(api_key, model_name, prompt_version)
        self.client = OpenAI(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def get_available_models(self) -> List[str]:
        """Return list of available OpenAI models."""
        return [
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ]

    def check_connection(self) -> bool:
        """Verify API key works."""
        try:
            # Try to list models as a connection check
            self.client.models.list()
            return True
        except Exception as e:
            print(f"OpenAI connection error: {e}")
            return False

    def send_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Send a message to OpenAI."""
        try:
            # Build messages array
            messages = [{"role": "system", "content": self.system_prompt}]

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": message})

            # Send to OpenAI
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error communicating with OpenAI: {str(e)}"

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
            messages = [{"role": "system", "content": self.system_prompt}]

            if conversation_history:
                messages.extend(conversation_history)

            messages.append({"role": "user", "content": message})

            # Convert tools to OpenAI format
            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": {
                            "type": "object",
                            "properties": tool.get("parameters", {}),
                            "required": tool.get("required", [])
                        }
                    }
                })

            # Send to OpenAI with tools
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
                temperature=0.7
            )

            # Handle tool calls
            while response.choices[0].message.tool_calls:
                # Add assistant's message to history
                messages.append(response.choices[0].message)

                # Execute each tool call
                for tool_call in response.choices[0].message.tool_calls:
                    function_name = tool_call.function.name
                    try:
                        function_args = json.loads(tool_call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        function_args = {}

                    # Execute the function
                    if tool_handler:
                        function_result = tool_handler(function_name, function_args)
                    else:
                        function_result = {"error": "No tool handler provided"}

                    # Add function result to messages
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_result)
                    })

                # Get next response
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                    temperature=0.7
                )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error with OpenAI function calling: {str(e)}"
