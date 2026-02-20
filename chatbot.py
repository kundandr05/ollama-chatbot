import requests
import json
from typing import Optional

class OllamaChatbot:
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama chatbot.
        
        Args:
            model: The model name to use (default: llama2)
            base_url: The base URL where Ollama is running (default: http://localhost:11434)
        """
        self.model = model
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
        self.conversation_history = []
    
    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models in Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    return [model["name"] for model in data["models"]]
            return []
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
    
    def chat(self, user_message: str, stream: bool = True) -> str:
        """
        Send a message to the chatbot and get a response.
        
        Args:
            user_message: The user's input message
            stream: Whether to stream the response (default: True)
        
        Returns:
            The chatbot's response as a string
        """
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Build conversation context
        context = self._build_context()
        
        try:
            payload = {
                "model": self.model,
                "prompt": context + user_message,
                "stream": stream,
                "temperature": 0.7,
            }
            
            response = requests.post(self.api_endpoint, json=payload)
            
            if stream:
                full_response = self._handle_streaming_response(response)
            else:
                full_response = self._handle_direct_response(response)
            
            self.conversation_history.append({"role": "assistant", "content": full_response})
            return full_response
        
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure Ollama is running on http://localhost:11434"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _build_context(self) -> str:
        """Build context from conversation history."""
        if not self.conversation_history:
            return ""
        
        context = ""
        for msg in self.conversation_history[-10:]:  # Keep last 10 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        return context + "Assistant: "
    
    def _handle_streaming_response(self, response) -> str:
        """Handle streaming response from Ollama."""
        full_response = ""
        try:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        chunk = data["response"]
                        full_response += chunk
                        print(chunk, end="", flush=True)
        except Exception as e:
            print(f"\nError processing stream: {e}")
        
        print()  # New line after streaming
        return full_response
    
    def _handle_direct_response(self, response) -> str:
        """Handle direct (non-streaming) response from Ollama."""
        try:
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            print(f"Error parsing response: {e}")
            return ""
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_history(self) -> list:
        """Get conversation history."""
        return self.conversation_history


def main():
    """Main function to run the chatbot."""
    print("=" * 60)
    print("Ollama Chatbot")
    print("=" * 60)
    
    # Initialize chatbot with default model
    chatbot = OllamaChatbot(model="llama2")
    
    # Check connection
    print("\nChecking connection to Ollama...")
    if not chatbot.check_connection():
        print("[ERROR] Cannot connect to Ollama!")
        print("Make sure Ollama is running. You can start it with: ollama serve")
        return
    
    print("[OK] Connected to Ollama!")
    
    # Show available models
    print("\nChecking available models...")
    models = chatbot.get_available_models()
    if models:
        print(f"Available models: {', '.join(models)}")
        # Use first available model if llama2 is not found
        if "llama2" not in models and models:
            chatbot.model = models[0]
            print(f"Using model: {chatbot.model}")
    else:
        print("No models found. Please pull a model with: ollama pull llama2")
        return
    
    print("\n" + "=" * 60)
    print("Chat started! Type 'quit' to exit, 'clear' to clear history")
    print("=" * 60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                break
            
            if user_input.lower() == "clear":
                chatbot.clear_history()
                print("Conversation history cleared.\n")
                continue
            
            print("\nBot: ", end="")
            chatbot.chat(user_input, stream=True)
            print()
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
