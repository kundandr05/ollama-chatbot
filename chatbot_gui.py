import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
from chatbot import OllamaChatbot

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Chatbot")
        self.root.geometry("700x600")
        
        self.chatbot = OllamaChatbot(model="llama2")
        self.setup_ui()
        self.check_connection()
        
    def setup_ui(self):
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state='disabled',
            font=("Arial", 10), bg="#f0f0f0"
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.input_field = tk.Entry(input_frame, font=("Arial", 11))
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.input_field.bind("<Return>", lambda e: self.send_message())
        
        self.send_button = tk.Button(
            input_frame, text="Send", command=self.send_message,
            bg="#4CAF50", fg="white", font=("Arial", 10, "bold")
        )
        self.send_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Bottom frame
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.clear_button = tk.Button(
            bottom_frame, text="Clear History", command=self.clear_history
        )
        self.clear_button.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(bottom_frame, text="", fg="gray")
        self.status_label.pack(side=tk.RIGHT)
        
    def check_connection(self):
        if self.chatbot.check_connection():
            models = self.chatbot.get_available_models()
            if models:
                if "llama2" not in models:
                    self.chatbot.model = models[0]
                self.append_message("System", f"Connected! Using model: {self.chatbot.model}")
            else:
                self.append_message("System", "No models found. Please pull a model.")
        else:
            self.append_message("System", "Cannot connect to Ollama. Make sure it's running.")
            
    def append_message(self, sender, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
        
    def send_message(self):
        message = self.input_field.get().strip()
        if not message:
            return
            
        self.input_field.delete(0, tk.END)
        self.append_message("You", message)
        self.send_button.config(state='disabled')
        self.status_label.config(text="Thinking...")
        
        threading.Thread(target=self.get_response, args=(message,), daemon=True).start()
        
    def get_response(self, message):
        response = self.chatbot.chat(message, stream=False)
        self.root.after(0, self.display_response, response)
        
    def display_response(self, response):
        self.append_message("Bot", response)
        self.send_button.config(state='normal')
        self.status_label.config(text="")
        self.input_field.focus()
        
    def clear_history(self):
        self.chatbot.clear_history()
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')
        self.append_message("System", "History cleared")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()
