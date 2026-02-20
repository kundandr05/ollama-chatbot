# Configuration file for Ollama Chatbot

# Ollama server configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama2"

# Chat settings
TEMPERATURE = 0.7  # Lower = more deterministic, Higher = more creative
MAX_TOKENS = 2048
CONTEXT_WINDOW = 10  # Number of previous messages to keep for context
STREAMING = True  # Enable streaming responses

# Available models and their specs
AVAILABLE_MODELS = {
    "llama2": {
        "size": "3.8 GB",
        "speed": "Fast",
        "quality": "Good",
        "use_case": "General purpose, most compatible"
    },
    "neural-chat": {
        "size": "4.8 GB",
        "speed": "Very Fast",
        "quality": "Good",
        "use_case": "Fast responses, good for chat"
    },
    "mistral": {
        "size": "4.1 GB",
        "speed": "Fast",
        "quality": "Excellent",
        "use_case": "Best balance of speed and quality"
    },
    "dolphin-mixtral": {
        "size": "26 GB",
        "speed": "Slower",
        "quality": "Excellent",
        "use_case": "Best quality, requires good GPU"
    },
}

# Model to use by default
MODEL_TO_USE = DEFAULT_MODEL
