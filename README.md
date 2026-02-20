# Ollama Chatbot

A simple Python chatbot that uses Ollama's local language models for conversational AI.

## Prerequisites

- **Ollama** installed on your desktop ([Download here](https://ollama.ai))
- **Python 3.7+** installed

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Ollama server:**
   ```bash
   ollama serve
   ```
   (Keep this running in a separate terminal)

3. **Pull a model (if not already done):**
   ```bash
   ollama pull llama2
   ```
   
   Other available models:
   - `ollama pull neural-chat` (faster, good for chat)
   - `ollama pull mistral` (powerful, more resources needed)
   - `ollama pull dolphin-mixtral` (good quality)

## Usage

Run the chatbot:
```bash
python chatbot.py
```

Then start chatting! Commands:
- Type your message and press Enter
- Type `clear` to clear conversation history
- Type `quit` to exit

### Example:
```
You: Hello, who are you?
Bot: I'm an AI assistant created by... [response streaming]

You: Can you help me with Python?
Bot: Of course! I can help with Python programming...
```

## Features

- ✅ Real-time response streaming
- ✅ Conversation history (for context)
- ✅ Multiple model support
- ✅ Connection checking
- ✅ Model availability detection
- ✅ Clean CLI interface

## Advanced Usage

### Using with a different model:

Edit `chatbot.py` and change the model name:
```python
chatbot = OllamaChatbot(model="neural-chat")
```

### Using in your own Python code:

```python
from chatbot import OllamaChatbot

# Create instance
bot = OllamaChatbot(model="llama2")

# Check connection
if bot.check_connection():
    # Get response
    response = bot.chat("What is Python?")
    print(response)
```

## Troubleshooting

**"Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`
- Check if it's running on the correct URL (default: http://localhost:11434)

**Models not showing up**
- Pull a model: `ollama pull llama2`
- List available models: `ollama list`

**Slow responses**
- Use a smaller/faster model like `neural-chat`
- Check your system resources

## Performance Tips

- **Fastest:** neural-chat (4.8 GB)
- **Balanced:** mistral (4.1 GB)
- **Best quality:** dolphin-mixtral (26 GB, needs good GPU)
- **Most compatible:** llama2 (3.8 GB)

## License

MIT
