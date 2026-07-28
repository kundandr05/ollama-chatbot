from flask import Flask, render_template, request, jsonify
import requests
import json
from typing import Optional

app = Flask(__name__)

import os

class OllamaChatbot:
    def __init__(self, model: str = "llama2", base_url: str = None):
        self.model = model
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.api_endpoint = f"{self.base_url}/api/generate"
        self.conversation_history = []
    
    def check_connection(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    return [model["name"] for model in data["models"]]
            return []
        except:
            return []
    
    def chat(self, user_message: str) -> str:
        """Send message and get response."""
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Build context
        context = self._build_context()
        
        try:
            payload = {
                "model": self.model,
                "prompt": context + user_message,
                "stream": False,
                "temperature": 0.7,
            }
            
            response = requests.post(self.api_endpoint, json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                full_response = data.get("response", "")
            else:
                full_response = "Error: Could not get response from Ollama"
            
            self.conversation_history.append({"role": "assistant", "content": full_response})
            return full_response
        
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be processing a large response."
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure it's running on http://localhost:11434"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _build_context(self) -> str:
        """Build context from history."""
        if not self.conversation_history:
            return ""
        
        context = ""
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n\n"
        
        return context
    
    def clear_history(self):
        """Clear conversation."""
        self.conversation_history = []


# Initialize chatbot
chatbot = OllamaChatbot(model="llama2")

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    """Check Ollama connection status."""
    connected = chatbot.check_connection()
    models = chatbot.get_available_models() if connected else []
    
    return jsonify({
        'connected': connected,
        'models': models,
        'current_model': chatbot.model
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    response = chatbot.chat(user_message)
    
    return jsonify({
        'user_message': user_message,
        'bot_response': response
    })

@app.route('/api/clear', methods=['POST'])
def clear():
    """Clear conversation history."""
    chatbot.clear_history()
    return jsonify({'status': 'cleared'})

@app.route('/api/set-model', methods=['POST'])
def set_model():
    """Set the model to use."""
    data = request.json
    model = data.get('model', 'llama2')
    chatbot.model = model
    return jsonify({'status': 'model set', 'model': model})

if __name__ == '__main__':
    print("Starting Ollama Web Chatbot...")
    print("Go to http://localhost:5000 in your browser")
    app.run(debug=True, host='localhost', port=5000)
