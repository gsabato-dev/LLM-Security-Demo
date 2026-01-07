"""
Google Vertex AI LLM Provider.
Uses GCP project credentials and billing.
"""
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content, FunctionDeclaration, Tool
from typing import List, Dict, Optional, Callable
from .base_provider import BaseLLMProvider


class VertexAIProvider(BaseLLMProvider):
    """Google Vertex AI implementation."""

    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash-001", project_id: str = None, location: str = "us-central1", prompt_version: str = "strict"):
        # For Vertex AI, we don't use api_key, but need project_id
        super().__init__(api_key or "", model_name, prompt_version)
        self.project_id = project_id
        self.location = location

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)

        # Create model with system instruction
        self.model = GenerativeModel(
            model_name=self.model_name,
            system_instruction=[self.system_prompt]
        )
        self.chat = None

    @property
    def provider_name(self) -> str:
        return "Google Vertex AI"

    def get_available_models(self) -> List[str]:
        """Return list of available Vertex AI models."""
        return [
            "gemini-2.0-flash-001",
            "gemini-2.5-flash-001",
            "gemini-2.5-pro-001",
            "gemini-1.5-flash-002",
            "gemini-1.5-pro-002"
        ]

    def check_connection(self) -> bool:
        """Verify Vertex AI connection works."""
        try:
            # Try to initialize a simple model
            test_model = GenerativeModel(model_name=self.model_name)
            return True
        except Exception as e:
            print(f"Vertex AI connection error: {e}")
            return False

    def send_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Send a message to Vertex AI."""
        try:
            # Build history from conversation
            history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append(
                        Content(
                            role=role,
                            parts=[Part.from_text(msg["content"])]
                        )
                    )

            # Start chat with history
            self.chat = self.model.start_chat(history=history)

            # Send message
            response = self.chat.send_message(message)
            return response.text

        except Exception as e:
            return f"Error communicating with Vertex AI: {str(e)}"

    def send_message_with_tools(
        self,
        message: str,
        tools: List[Dict],
        conversation_history: List[Dict[str, str]] = None,
        tool_handler: Callable = None
    ) -> str:
        """Send a message with function calling."""
        try:
            # Convert tools to Vertex AI format
            vertex_tools = []
            function_declarations = []

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

                function_declarations.append(
                    FunctionDeclaration(
                        name=tool["name"],
                        description=tool["description"],
                        parameters=params
                    )
                )

            vertex_tools = [Tool(function_declarations=function_declarations)]

            # Create model with tools
            model_with_tools = GenerativeModel(
                model_name=self.model_name,
                system_instruction=[self.system_prompt],
                tools=vertex_tools
            )

            # Build history
            history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append(
                        Content(
                            role=role,
                            parts=[Part.from_text(msg["content"])]
                        )
                    )

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
                    if part.function_call:
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
                            Part.from_function_response(
                                name=function_name,
                                response={"result": function_result}
                            )
                        )
                        break

                if not has_function_call:
                    break

                iteration += 1

            # Extract text from final response
            return response.text

        except Exception as e:
            return f"Error with Vertex AI function calling: {str(e)}"

    def reset_chat(self):
        """Reset chat history."""
        self.chat = None
