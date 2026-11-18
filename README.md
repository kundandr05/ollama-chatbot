# 🤖 Ollama Web & CLI AI Chatbot

[![Live Demo](https://img.shields.io/badge/Demo-kundan--ollama--chatbot.vercel.app-blue?style=for-the-badge&logo=vercel)](https://kundan-ollama-chatbot.vercel.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-kundandr05%2Follama--chatbot-black?style=for-the-badge&logo=github)](https://github.com/kundandr05/ollama-chatbot)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-orange.svg?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

A full-featured AI conversational assistant powered by local **Ollama** models, featuring a modern web interface, live internet search, voice input/output, dark mode, and seamless cloud deployment on Vercel.

---

## 🌐 Live Web Demo

You can try the live web chatbot hosted on Vercel:

👉 **[https://kundan-ollama-chatbot.vercel.app/](https://kundan-ollama-chatbot.vercel.app/)**

> **Note:** To connect the live Vercel cloud frontend to your local Ollama engine, expose your local Ollama port via `ngrok` (or set `OLLAMA_API_URL` in your Vercel project environment variables).

---

## ✨ Features

- 🌐 **Live Web Search (Real-time Answers):** Toggleable Google search integration allows the AI to provide up-to-date facts, news, and current events beyond training data limits.
- 🎙️ **Voice Chat (STT & TTS):**
  - **Speech-to-Text:** Click the microphone button to dictate your prompts hands-free.
  - **Text-to-Speech:** Click the speaker icon on any assistant message to listen to the response out loud.
- 🌓 **Dark & Light Mode:** Seamless theme toggle with persistent preferences and glassmorphism styling.
- 📝 **Markdown & Code Highlighting:** Automatic formatting for markdown responses with syntax highlighting and a 1-click code block copy button.
- 🎭 **Custom System Persona:** Customize the AI's identity, personality, and instructions directly from the web settings bar.
- 🔄 **Dynamic Model Switching:** Switch between any locally installed Ollama models (`llama3.2`, `llama2`, `mistral`, `neural-chat`, etc.) without restarting the server.
- ⚡ **Typing Indicators & Live Connection Status:** Real-time visual feedback for server health and token generation.
- 💻 **Multiple Interfaces:**
  - **Web App:** Flask + modern responsive frontend (deployable to Vercel).
  - **Desktop GUI:** Tkinter-based desktop chatbot (`gui_chatbot.py`).
  - **CLI:** Fast terminal client (`chatbot.py`).

---

## 🛠️ Architecture

```
[ User Browser / Web Client ]
              │
              ▼
   https://kundan-ollama-chatbot.vercel.app
         (Vercel Serverless / Flask)
              │
              │  OLLAMA_API_URL (via ngrok tunnel)
              ▼
    [ Local Machine : 11434 ]
              │
              ▼
        [ Ollama Engine ]
   (llama3.2, mistral, llama2, etc.)
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.8+** installed ([python.org](https://www.python.org/))
- **Ollama** installed ([ollama.ai](https://ollama.ai))

### 2. Install Ollama & Pull Models

Start the Ollama server:
```bash
ollama serve
```

In a new terminal, pull your preferred models:
```bash
ollama pull llama3.2
ollama pull llama2
```

### 3. Installation

Clone this repository:
```bash
git clone https://github.com/kundandr05/ollama-chatbot.git
cd ollama-chatbot
```

Create a virtual environment and install dependencies:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 🖥️ Running the Chatbot

### Option A: Web Interface (Local)

Run the Flask server:
```bash
python web_chatbot.py
```
Open your browser and navigate to: `http://localhost:5000`

### Option B: Terminal CLI

```bash
python chatbot.py
```
Commands:
- Type your message and press **Enter**
- Type `clear` to reset chat history
- Type `quit` to exit

### Option C: Desktop GUI

```bash
python gui_chatbot.py
```

---

## ☁️ Deploying to Vercel

1. Fork or push this repository to your GitHub account:
   `https://github.com/kundandr05/ollama-chatbot`
2. Import the repository into [Vercel](https://vercel.com).
3. Set the Environment Variable in your Vercel Project Settings:
   - `OLLAMA_API_URL`: Your public ngrok tunnel URL (e.g. `https://xxxx-xx-xx.ngrok-free.app`)
4. Deploy! Your app will be live at:
   `https://kundan-ollama-chatbot.vercel.app/`

---

## 📁 Project Structure

```
ollama-chatbot/
├── templates/
│   └── index.html             # Modern Web UI (Dark mode, Voice STT/TTS, Markdown)
├── web_chatbot.py             # Flask Web Application + Web Search integration
├── chatbot.py                 # Core CLI Chatbot engine
├── chatbot_gui.py             # Basic desktop interface
├── gui_chatbot.py             # Advanced desktop interface
├── config.py                  # Default system configuration
├── requirements.txt           # Production dependencies for Web & Vercel
├── vercel.json                # Vercel serverless deployment config
└── README.md                  # Project documentation
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Made with ❤️ by [kundandr05](https://github.com/kundandr05)
