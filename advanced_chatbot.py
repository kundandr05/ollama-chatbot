"""
Advanced Ollama Chatbot with additional features:
- Save/load conversation history
- Custom system prompts
- Different chat modes
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List


class AdvancedOllamaChatbot:
    def __init__(
        self,
        model: str = "llama2",
        base_url: str = "http://localhost:11434",
        system_prompt: str = None,
        history_file: str = None
    ):
        """
        Initialize advanced chatbot with history saving and system prompts.
        
        Args:
            model: The model name to use
            base_url: Ollama server URL
            system_prompt: Custom system prompt
            history_file: File to save conversation history
        """
        self.model = model
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
        self.conversation_history = []
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.history_file = history_file or f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    def set_system_prompt(self, prompt: str):
        """Set a custom system prompt."""
        self.system_prompt = prompt
    
    def chat(self, user_message: str, stream: bool = True) -> str:
        """Send message and get response."""
        self.conversation_history.append({"role": "user", "content": user_message})
        
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
            return "Error: Cannot connect to Ollama."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _build_context(self) -> str:
        """Build context with system prompt."""
        context = f"System: {self.system_prompt}\n\n"
        
        if self.conversation_history:
            for msg in self.conversation_history[-10:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"
        
        return context + "Assistant: "
    
    def _handle_streaming_response(self, response) -> str:
        """Handle streaming response."""
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
            print(f"\nError: {e}")
        
        print()
        return full_response
    
    def _handle_direct_response(self, response) -> str:
        """Handle direct response."""
        try:
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def save_history(self):
        """Save conversation history to file."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.conversation_history, f, indent=2)
            print(f"✓ History saved to {self.history_file}")
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        """Load conversation history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    self.conversation_history = json.load(f)
                print(f"✓ History loaded from {self.history_file}")
            else:
                print(f"History file not found: {self.history_file}")
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def export_history(self, filename: str):
        """Export history to a specific file."""
        try:
            with open(filename, "w") as f:
                json.dump(self.conversation_history, f, indent=2)
            print(f"✓ Exported to {filename}")
        except Exception as e:
            print(f"Error exporting: {e}")
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_stats(self) -> dict:
        """Get conversation statistics."""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m["role"] == "assistant"]),
            "model": self.model,
            "system_prompt": self.system_prompt,
        }


class ChatModes:
    """Pre-configured chat modes with different system prompts."""
    
    CODE_HELPER = "You are an expert programmer. Help the user with coding questions, debugging, and best practices."
    TEACHER = "You are a knowledgeable teacher. Explain concepts clearly and provide examples."
    CREATIVE = "You are a creative writing assistant. Help with storytelling, poetry, and creative expression."
    ANALYST = "You are a data analyst. Help analyze information, identify patterns, and provide insights."
    MEDICAL = "You are a health information assistant. Provide general health information (not medical advice)."


def main():
    """Run advanced chatbot with system prompt selection."""
    print("=" * 60)
    print("Advanced Ollama Chatbot")
    print("=" * 60)
    
    # Select chat mode
    print("\nSelect chat mode:")
    print("1. General Assistant (default)")
    print("2. Code Helper")
    print("3. Teacher")
    print("4. Creative Writer")
    print("5. Analyst")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    modes = {
        "1": ("General Assistant", "You are a helpful AI assistant."),
        "2": ("Code Helper", ChatModes.CODE_HELPER),
        "3": ("Teacher", ChatModes.TEACHER),
        "4": ("Creative Writer", ChatModes.CREATIVE),
        "5": ("Analyst", ChatModes.ANALYST),
    }
    
    mode_name, system_prompt = modes.get(choice, ("General Assistant", "You are a helpful AI assistant."))
    
    # Initialize chatbot
    chatbot = AdvancedOllamaChatbot(model="llama2", system_prompt=system_prompt)
    
    print(f"\n✓ Mode: {mode_name}")
    print("=" * 60)
    print("Commands: 'quit' to exit, 'save' to save history, 'stats' for statistics")
    print("=" * 60 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                save = input("Save history? (y/n): ").lower()
                if save == "y":
                    chatbot.save_history()
                print("Goodbye!")
                break
            
            if user_input.lower() == "save":
                chatbot.save_history()
                continue
            
            if user_input.lower() == "stats":
                stats = chatbot.get_stats()
                print("\nConversation Stats:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
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
