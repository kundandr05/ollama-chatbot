from flask import Flask, render_template, request, jsonify
import requests
import json
from typing import Optional
from googlesearch import search

app = Flask(__name__)

import os

class OllamaChatbot:
    def __init__(self, model: str = "llama2", base_url: str = None):
        self.model = model
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.api_endpoint = f"{self.base_url}/api/generate"
        self.system_prompt = ""
        self.conversation_history = []
    
    def check_connection(self) -> bool:
        """Check if Ollama is running."""
        try:
            headers = {"ngrok-skip-browser-warning": "true"}
            response = requests.get(f"{self.base_url}/api/tags", headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models."""
        try:
            headers = {"ngrok-skip-browser-warning": "true"}
            response = requests.get(f"{self.base_url}/api/tags", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    return [model["name"] for model in data["models"]]
            return []
        except:
            return []
    
    def chat(self, user_message: str, use_web_search: bool = False) -> str:
        """Send message and get response."""
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Build context
        context = self._build_context()
        
        # Optionally perform web search
        web_context = ""
        if use_web_search:
            try:
                results = search(user_message, num_results=3, advanced=True)
                if results:
                    web_context = "Here is some live information from the web to help you answer:\n"
                    for r in results:
                        web_context += f"- {r.title}: {r.description}\n"
                    web_context += "\n"
            except Exception as e:
                print(f"Web search error: {e}")
        
        try:
            # Build full prompt including system message if set
            full_prompt = context + web_context + user_message
            if self.system_prompt:
                full_prompt = f"System: {self.system_prompt}\n\n{full_prompt}"
                
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "temperature": 0.7,
            }
            
            headers = {"ngrok-skip-browser-warning": "true"}
            response = requests.post(self.api_endpoint, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                full_response = data.get("response", "")
            else:
                full_response = f"Error: Could not get response. Status: {response.status_code}, Text: {response.text[:100]}"
            
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
    use_web_search = data.get('use_web_search', False)
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    response = chatbot.chat(user_message, use_web_search)
    
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

@app.route('/api/set-system', methods=['POST'])
def set_system():
    """Set the system persona prompt."""
    data = request.json
    system_prompt = data.get('prompt', '').strip()
    chatbot.system_prompt = system_prompt
    return jsonify({'status': 'system prompt set', 'prompt': system_prompt})

if __name__ == '__main__':
    print("Starting Ollama Web Chatbot...")
    print("Go to http://localhost:5000 in your browser")
    app.run(debug=True, host='localhost', port=5000)
