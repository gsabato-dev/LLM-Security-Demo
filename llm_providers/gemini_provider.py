"""
Google Gemini LLM Provider.
"""
import google.generativeai as genai
from google.generativeai import types
from typing import List, Dict, Optional, Callable
from .base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini implementation."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash", prompt_version: str = "strict"):
        super().__init__(api_key, model_name, prompt_version)
        genai.configure(api_key=self.api_key)

        # Configure model with system instruction
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_prompt
        )
        self.chat = None

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    def get_available_models(self) -> List[str]:
        """Return list of available Gemini models."""
        return [
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-exp-1206",
            "gemini-pro-latest",
            "gemini-flash-latest"
        ]

    def check_connection(self) -> bool:
        """Verify API key works."""
        try:
            # Try to list models as a connection check
            list(genai.list_models())
            return True
        except Exception as e:
            print(f"Gemini connection error: {e}")
            return False

    def send_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Send a message to Gemini."""
        try:
            # Build history from conversation
            history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })

            # Start chat with history
            self.chat = self.model.start_chat(history=history)

            # Send message
            response = self.chat.send_message(message)
            return response.text

        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

    def send_message_with_tools(
        self,
        message: str,
        tools: List[Dict],
        conversation_history: List[Dict[str, str]] = None,
        tool_handler: Callable = None
    ) -> str:
        """Send a message with function calling."""
        try:
            # Convert tools to Gemini format
            gemini_tools = []
            for tool in tools:
                # Build parameter schema
                params = {
                    "type": "object",
                    "properties": {},
                    "required": tool.get("required", [])
                }

                for param_name, param_info in tool.get("parameters", {}).items():
                    params["properties"][param_name] = {
                        "type": param_info.get("type", "string"),
                        "description": param_info.get("description", "")
                    }

                gemini_tools.append({
                    "function_declarations": [{
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": params
                    }]
                })

            # Create model with tools
            model_with_tools = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.system_prompt,
                tools=gemini_tools
            )

            # Build history
            history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })

            # Start chat
            chat = model_with_tools.start_chat(history=history)

            # Send message
            response = chat.send_message(message)

            # Handle function calls
            max_iterations = 5
            iteration = 0

            while iteration < max_iterations:
                # Check if there are function calls in the response
                if not response.candidates or not response.candidates[0].content.parts:
                    break

                has_function_call = False
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        has_function_call = True
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)

                        # Execute the function
                        if tool_handler:
                            function_result = tool_handler(function_name, function_args)
                        else:
                            function_result = {"error": "No tool handler provided"}

                        # Send function result back
                        response = chat.send_message(
                            types.Content(
                                parts=[types.Part(
                                    function_response=types.FunctionResponse(
                                        name=function_name,
                                        response={"result": function_result}
                                    )
                                )]
                            )
                        )
                        break

                if not has_function_call:
                    break

                iteration += 1

            # Extract text from final response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        return part.text

            return response.text if hasattr(response, 'text') else str(response)

        except Exception as e:
            return f"Error with Gemini function calling: {str(e)}"

    def _convert_type(self, type_str: str):
        """Convert JSON schema type to Gemini type."""
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT
        }
        return type_mapping.get(type_str.lower(), genai.protos.Type.STRING)

    def reset_chat(self):
        """Reset chat history."""
        self.chat = None
