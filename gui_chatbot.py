import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import requests
import json
from typing import Optional
from datetime import datetime
import os
from deep_translator import GoogleTranslator

class GUIChatbot(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("chatbot")
        self.geometry("1100x800")
        
        # Neon theme colors - MUST be defined first
        self.neon_cyan = "#00ffff"
        self.neon_magenta = "#ff00ff"
        self.neon_green = "#39ff14"
        self.neon_pink = "#ff10f0"
        self.neon_yellow = "#ffff00"
        self.neon_blue = "#00d4ff"
        self.bg_dark = "#0a0e27"
        self.bg_darker = "#050810"
        
        # Light theme colors
        self.light_bg = "#ffffff"
        self.light_bg_darker = "#f5f5f5"
        self.light_text = "#333333"
        self.light_text_dim = "#666666"
        
        # Theme settings
        self.dark_mode = True
        
        # Configure style
        self.style = ttk.Style()
        self.update_theme_colors()
        self.set_theme(self.dark_mode)
        
        # Ollama settings
        self.model = "llama2"
        self.ollama_host = "localhost"
        self.ollama_port = "11434"
        self.base_url = f"http://{self.ollama_host}:{self.ollama_port}"
        self.temperature = 0.7
        self.conversation_history = []
        self.is_loading = False
        self.available_models = []
        self.current_language = "English"
        self.languages = ["English", "Hindi", "Tamil", "Telugu", "Kannada"]
        self.use_streaming = True
        self.recording = False  # Voice input state
        
        # We will instantiate GoogleTranslator when needed to handle different source/dest languages
        
        # Personalization settings
        self.user_name = "User"
        self.bot_name = "ChatBot"
        self.system_prompt = "You are a helpful and friendly AI assistant."
        self.bot_personality = "Friendly"
        self.personalities = ["Friendly", "Professional", "Creative", "Sarcastic", "Educational"]
        self.personality_prompts = {
            "Friendly": "You are a warm, helpful, and conversational AI assistant. Be approachable and kind.",
            "Professional": "You are a professional and formal AI assistant. Provide accurate, well-structured responses.",
            "Creative": "You are a creative and imaginative AI assistant. Think outside the box and suggest innovative ideas.",
            "Sarcastic": "You are a witty and slightly sarcastic AI assistant. Use humor while being helpful.",
            "Educational": "You are an educational AI tutor. Explain concepts clearly and help users learn."
        }
        
        # File upload settings
        self.current_file_path = None
        self.current_file_content = None
        self.current_file_name = "No file loaded"
        
        # Response control
        self.stop_response = False  # Flag to stop current response
        
        # Load personalization settings early
        self.load_personalization_settings()
        
        # UI setup
        self.setup_ui()
        
        # Update API settings in UI after creation
        self.host_var.set(self.ollama_host)
        self.port_var.set(self.ollama_port)
        
        self.load_models()
        self.check_connection()
        self.after(5000, self.check_connection_async)
        
        # Keyboard shortcuts
        self.bind('<Control-s>', lambda e: self.save_chat())
        self.bind('<Control-o>', lambda e: self.load_chat())
        self.bind('<Control-f>', lambda e: self.show_search())
        self.bind('<Control-e>', lambda e: self.export_chat())
        self.bind('<Control-t>', lambda e: self.toggle_theme())
        self.bind('<Control-h>', lambda e: self.show_shortcuts())
    
    def set_theme(self, is_dark):
        """Set background color based on theme"""
        self.dark_mode = is_dark
        bg_color = self.bg_dark if is_dark else self.light_bg
        self.configure(bg=bg_color)
    
    def update_theme_colors(self):
        """Update all theme colors"""
        if self.dark_mode:
            self.style.theme_use('clam')
            self.style.configure('TFrame', background=self.bg_dark)
            self.style.configure('TLabel', background=self.bg_dark, foreground=self.neon_cyan)
            self.style.configure('Header.TLabel', background=self.bg_darker, foreground=self.neon_pink, font=('Segoe UI', 14, 'bold'))
            self.style.configure('TCombobox', fieldbackground=self.bg_darker, background=self.bg_darker, foreground=self.neon_cyan)
            self.style.configure('TButton', background=self.bg_darker, foreground=self.neon_cyan, borderwidth=2, relief='solid')
            self.style.map('TButton', background=[('active', self.bg_darker), ('pressed', self.neon_cyan)], foreground=[('active', self.neon_magenta), ('pressed', self.bg_dark)])
            
            self.input_bg = self.bg_darker
            self.input_fg = self.neon_cyan
            self.chat_bg = self.bg_darker
            self.chat_fg = self.neon_cyan
        else:
            self.style.theme_use('clam')
            self.style.configure('TFrame', background=self.light_bg)
            self.style.configure('TLabel', background=self.light_bg, foreground=self.light_text)
            self.style.configure('Header.TLabel', background=self.light_bg_darker, foreground='#0066cc', font=('Segoe UI', 14, 'bold'))
            self.style.configure('TCombobox', fieldbackground=self.light_bg_darker, background=self.light_bg_darker, foreground=self.light_text)
            self.style.configure('TButton', background=self.light_bg_darker, foreground=self.light_text, borderwidth=1, relief='solid')
            self.style.map('TButton', background=[('active', '#e0e0e0'), ('pressed', '#d0d0d0')])
            
            self.input_bg = self.light_bg_darker
            self.input_fg = self.light_text
            self.chat_bg = self.light_bg
            self.chat_fg = self.light_text
    
    def setup_ui(self):
        """Setup all UI components with modern ChatGPT-like design"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Header (minimal)
        self.setup_header(main_frame)
        
        # Chat display (main focus, takes most space)
        self.setup_chat_display(main_frame)
        
        # Input area (bottom) - now includes file status inline
        self.setup_input_area(main_frame)
        
        # Status bar (minimal)
        self.setup_status_bar(main_frame)
        
        # Settings panel (collapsible, hidden by default)
        self.setup_settings_panel(main_frame)
    
    def setup_header(self, parent):
        """Setup minimal header"""
        header_frame = ttk.Frame(parent, relief=tk.FLAT)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Left side - title
        header_label = ttk.Label(header_frame, text="🤖 CHATBOT", style='Header.TLabel')
        header_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=10)
        
        # Right side - status and buttons
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.status_label = ttk.Label(right_frame, text="🔴 Disconnected")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        settings_btn = ttk.Button(right_frame, text="⚙️", command=self.toggle_settings_panel)
        settings_btn.pack(side=tk.LEFT, padx=2)
        
        theme_btn = ttk.Button(right_frame, text="🌙", command=self.toggle_theme)
        theme_btn.pack(side=tk.LEFT, padx=2)
        
        help_btn = ttk.Button(right_frame, text="❓", command=self.show_shortcuts)
        help_btn.pack(side=tk.LEFT, padx=2)
    
    def toggle_settings_panel(self):
        """Toggle settings panel visibility"""
        if self.settings_frame.winfo_viewable():
            self.settings_frame.pack_forget()
        else:
            self.settings_frame.pack(fill=tk.X, padx=15, pady=5, after=self.settings_frame.master.winfo_children()[0])
    
    def setup_settings_panel(self, parent):
        """Setup collapsible settings panel (hidden by default)"""
        self.settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings & Personalization", relief=tk.FLAT)
        self.settings_frame.pack(fill=tk.X, padx=15, pady=5)
        self.settings_frame.pack_forget()  # Hide by default
        
        # Create settings content
        # Row 0: User Info (compact)
        row0 = ttk.Frame(self.settings_frame)
        row0.pack(fill=tk.X, pady=2)
        
        ttk.Label(row0, text="Your Name:").pack(side=tk.LEFT, padx=3)
        self.user_name_var = tk.StringVar(value=self.user_name)
        user_entry = ttk.Entry(row0, textvariable=self.user_name_var, width=12)
        user_entry.pack(side=tk.LEFT, padx=3)
        user_entry.bind('<FocusOut>', self.on_user_name_changed)
        
        ttk.Label(row0, text="Bot Name:").pack(side=tk.LEFT, padx=3)
        self.bot_name_var = tk.StringVar(value=self.bot_name)
        bot_entry = ttk.Entry(row0, textvariable=self.bot_name_var, width=12)
        bot_entry.pack(side=tk.LEFT, padx=3)
        bot_entry.bind('<FocusOut>', self.on_bot_name_changed)
        
        ttk.Label(row0, text="Personality:").pack(side=tk.LEFT, padx=3)
        self.personality_var = tk.StringVar(value=self.bot_personality)
        personality_dropdown = ttk.Combobox(row0, textvariable=self.personality_var, values=self.personalities, state='readonly', width=12)
        personality_dropdown.pack(side=tk.LEFT, padx=3)
        personality_dropdown.bind('<<ComboboxSelected>>', self.on_personality_changed)
        
        # Row 1: Model and Language
        row1 = ttk.Frame(self.settings_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Model:").pack(side=tk.LEFT, padx=3)
        self.model_var = tk.StringVar(value="llama2")
        self.model_dropdown = ttk.Combobox(row1, textvariable=self.model_var, values=["Loading..."], state='readonly', width=15)
        self.model_dropdown.pack(side=tk.LEFT, padx=3)
        self.model_dropdown.bind('<<ComboboxSelected>>', self.on_model_changed)
        
        ttk.Label(row1, text="Language:").pack(side=tk.LEFT, padx=3)
        self.lang_var = tk.StringVar(value="English")
        self.lang_dropdown = ttk.Combobox(row1, textvariable=self.lang_var, values=self.languages, state='readonly', width=12)
        self.lang_dropdown.pack(side=tk.LEFT, padx=3)
        self.lang_dropdown.bind('<<ComboboxSelected>>', self.on_language_changed)
        
        # Row 2: Temperature and API settings
        row2 = ttk.Frame(self.settings_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="Temp:").pack(side=tk.LEFT, padx=3)
        self.temp_var = tk.DoubleVar(value=0.7)
        self.temp_scale = ttk.Scale(row2, from_=0, to=2, orient=tk.HORIZONTAL, variable=self.temp_var, command=self.on_temperature_changed, length=80)
        self.temp_scale.pack(side=tk.LEFT, padx=3)
        self.temp_label = ttk.Label(row2, text="0.7", width=4)
        self.temp_label.pack(side=tk.LEFT, padx=3)
        
        self.streaming_var = tk.BooleanVar(value=True)
        self.streaming_check = ttk.Checkbutton(row2, text="Stream", variable=self.streaming_var)
        self.streaming_check.pack(side=tk.LEFT, padx=3)
        
        ttk.Label(row2, text="Host:").pack(side=tk.LEFT, padx=3)
        self.host_var = tk.StringVar(value="localhost")
        self.host_entry = ttk.Entry(row2, textvariable=self.host_var, width=12)
        self.host_entry.pack(side=tk.LEFT, padx=3)
        self.host_entry.bind('<FocusOut>', self.on_url_changed)
        
        ttk.Label(row2, text="Port:").pack(side=tk.LEFT, padx=3)
        self.port_var = tk.StringVar(value="11434")
        self.port_entry = ttk.Entry(row2, textvariable=self.port_var, width=8)
        self.port_entry.pack(side=tk.LEFT, padx=3)
        self.port_entry.bind('<FocusOut>', self.on_url_changed)
        
        test_btn = ttk.Button(row2, text="🔗 Test", command=self.test_connection)
        test_btn.pack(side=tk.LEFT, padx=3)
        
        # Row 3: System Prompt
        row3 = ttk.Frame(self.settings_frame)
        row3.pack(fill=tk.X, pady=2, padx=3)
        
        ttk.Label(row3, text="System Prompt:").pack(side=tk.TOP, anchor=tk.W)
        
        self.system_prompt_text = tk.Text(row3, height=2, font=('Consolas', 8), wrap=tk.WORD, bg=self.input_bg, fg=self.input_fg)
        self.system_prompt_text.pack(fill=tk.X, pady=2)
        self.system_prompt_text.insert(tk.END, self.system_prompt)
        
        update_prompt_btn = ttk.Button(row3, text="🔄 Update", command=self.update_system_prompt)
        update_prompt_btn.pack(anchor=tk.E, padx=3, pady=2)
    
    def on_url_changed(self, event=None):
        """Handle host/port change"""
        self.ollama_host = self.host_var.get() or "localhost"
        self.ollama_port = self.port_var.get() or "11434"
        self.base_url = f"http://{self.ollama_host}:{self.ollama_port}"
        self.status_bar.config(text=f"🔧 URL updated: {self.base_url}")
    
    def test_connection(self):
        """Test connection to Ollama server"""
        self.on_url_changed()
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if response.status_code == 200:
                messagebox.showinfo("✅ Connection Success", f"Connected to Ollama at {self.base_url}")
                self.status_bar.config(text="✅ Connection verified")
                self.load_models()
            else:
                messagebox.showerror("❌ Connection Failed", f"Server returned: {response.status_code}")
                self.status_bar.config(text="❌ Connection failed")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("❌ Connection Error", f"Cannot connect to {self.base_url}\n\nMake sure Ollama is running on that address.")
            self.status_bar.config(text="❌ Connection error")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error: {str(e)}")
            self.status_bar.config(text=f"❌ Error: {str(e)}")
    
    def setup_chat_display(self, parent):
        """Setup chat display area"""
        self.chat_display_frame = ttk.Frame(parent)
        self.chat_display_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_display_frame, wrap=tk.WORD, font=('Consolas', 10), bg=self.chat_bg, fg=self.chat_fg,
            relief=tk.SUNKEN, bd=2, padx=10, pady=10, undo=False, maxundo=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure text tags
        self.chat_display.tag_configure("user", foreground=self.neon_green if self.dark_mode else "#0066cc", font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure("bot", foreground=self.neon_cyan if self.dark_mode else self.light_text, font=('Consolas', 10))
        self.chat_display.tag_configure("error", foreground=self.neon_pink if self.dark_mode else "#cc0000", font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure("loading", foreground=self.neon_yellow if self.dark_mode else "#ff9900", font=('Consolas', 9, 'italic'))
        self.chat_display.tag_configure("highlight", background=self.neon_yellow if self.dark_mode else "#ffff00", foreground="black")
        
        # Right-click context menu
        self.chat_display.bind("<Button-3>", self.show_context_menu)
        
        self.add_message("👋 Welcome! I'm an AI assistant powered by Ollama. How can I help you?", "bot")
    
    def setup_file_panel(self, parent):
        """Setup file upload panel (simple)"""
        pass  # Now integrated inline in input area
    
    def setup_input_area(self, parent):
        """Setup input area with ChatGPT-style design + file status inline"""
        # File status bar (inline, above input)
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill=tk.X, padx=15, pady=(10, 3))
        self.file_label = ttk.Label(file_frame, text="📄 No file loaded", font=('Segoe UI', 8))
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        # Main input container
        input_container = ttk.Frame(parent)
        input_container.pack(fill=tk.X, padx=15, pady=(3, 15))
        
        # Input field with placeholder
        self.input_field = tk.Text(
            input_container, height=3, font=('Segoe UI', 11), wrap=tk.WORD,
            bg=self.input_bg, fg=self.input_fg, insertbackground=self.input_fg, 
            undo=True, maxundo=20, relief=tk.SOLID, bd=1, padx=12, pady=10
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.input_field.bind('<Control-Return>', lambda e: self.send_message())
        
        # Add placeholder
        self.input_field.insert("1.0", "Ask anything...")
        self.input_field.config(fg="#888888")
        self.input_field.bind('<FocusIn>', self.on_input_focus_in)
        self.input_field.bind('<FocusOut>', self.on_input_focus_out)
        
        # Buttons (vertical stack on the right)
        button_frame = ttk.Frame(input_container)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_btn = ttk.Button(button_frame, text="📤", command=self.send_message, width=4)
        self.send_btn.pack(side=tk.TOP, padx=(0, 0), pady=(0, 8))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️", command=self.stop_response_handler, width=4)
        self.stop_btn.pack(side=tk.TOP, padx=(0, 0), pady=(0, 8))
        
        self.voice_btn = ttk.Button(button_frame, text="🎤", command=self.toggle_voice_input, width=4)
        self.voice_btn.pack(side=tk.TOP, padx=(0, 0), pady=(0, 8))
        
        upload_btn = ttk.Button(button_frame, text="📁", command=self.upload_file, width=4)
        upload_btn.pack(side=tk.TOP)
    
    def on_input_focus_in(self, event):
        """Handle input field focus - clear placeholder"""
        if self.input_field.get("1.0", tk.END).strip() == "Ask anything...":
            self.input_field.delete("1.0", tk.END)
            self.input_field.config(fg=self.input_fg)
    
    def on_input_focus_out(self, event):
        """Handle input field blur - show placeholder if empty"""
        if not self.input_field.get("1.0", tk.END).strip():
            self.input_field.insert("1.0", "Ask anything...")
            self.input_field.config(fg="#888888")
    
    def upload_file(self):
        """Open file dialog and load file - simplified with better encoding handling"""
        filetypes = [
            ("All Text Files", "*.txt *.md *.csv *.json *.log"),
            ("Text Files", "*.txt"),
            ("Markdown Files", "*.md"),
            ("CSV Files", "*.csv"),
            ("JSON Files", "*.json"),
            ("All Files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select a file to analyze",
            filetypes=filetypes
        )
        
        if not filename:
            return
        
        try:
            self.current_file_path = filename
            self.current_file_name = filename.split("\\")[-1]
            
            # Try multiple encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
            self.current_file_content = None
            
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding) as f:
                        self.current_file_content = f.read()
                    break
                except (UnicodeDecodeError, UnicodeEncodeError):
                    continue
            
            if self.current_file_content is None:
                raise Exception("Could not read file with any supported encoding")
            
            # Truncate if too long
            max_length = 5000
            if len(self.current_file_content) > max_length:
                self.current_file_content = self.current_file_content[:max_length] + f"\n\n[... truncated. Full length: {len(self.current_file_content)} chars ...]"
            
            self.file_label.config(text=f"✅ {self.current_file_name}")
            self.status_bar.config(text=f"📄 Loaded: {self.current_file_name}")
            self.add_message(f"📄 Loaded: {self.current_file_name}", "bot")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{str(e)}")
            self.status_bar.config(text="❌ Error loading file")
    
    def clear_file(self):
        """Clear the loaded file"""
        self.current_file_path = None
        self.current_file_content = None
        self.current_file_name = "No file loaded"
        self.file_label.config(text="📄 No file loaded")
        self.status_bar.config(text="File cleared")
        self.add_message("File cleared ✓", "bot")
    
    def setup_status_bar(self, parent):
        """Setup status bar"""
        self.status_bar = ttk.Label(parent, text="🚀 Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, padx=0, pady=0)
    
    def add_message(self, message: str, sender: str = "bot"):
        """Add message to chat display efficiently"""
        self.chat_display.config(state=tk.NORMAL)
        
        labels = {
            "user": f"{self.user_name}: ", 
            "bot": f"{self.bot_name}: ", 
            "error": "Error: ", 
            "loading": "Thinking"
        }
        label = labels.get(sender, "")
        
        self.chat_display.insert(tk.END, label, sender)
        self.chat_display.insert(tk.END, message + "\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.after(10, lambda: self.chat_display.see(tk.END))
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copy", command=lambda: self.copy_selected())
        menu.add_command(label="Select All", command=lambda: self.chat_display.tag_add(tk.SEL, "1.0", tk.END))
        menu.post(event.x_root, event.y_root)
    
    def copy_selected(self):
        """Copy selected text to clipboard"""
        try:
            self.clipboard_clear()
            self.clipboard_append(self.chat_display.get(tk.SEL_FIRST, tk.SEL_LAST))
            self.status_bar.config(text="✅ Copied to clipboard")
        except:
            messagebox.showwarning("Copy", "No text selected")
    
    def on_model_changed(self, event):
        """Handle model change"""
        self.model = self.model_var.get()
        self.status_bar.config(text=f"⚙️ Model changed to: {self.model}")
    
    def on_language_changed(self, event):
        """Handle language change"""
        self.current_language = self.lang_var.get()
        self.status_bar.config(text=f"🌍 Language: {self.current_language}")
    
    def on_temperature_changed(self, value):
        """Handle temperature change"""
        self.temperature = float(value)
        self.temp_label.config(text=f"{self.temperature:.2f}")
    
    def save_settings(self):
        """Save current settings"""
        self.on_url_changed()
        self.save_personalization_settings()
        messagebox.showinfo("Settings", "Settings saved successfully!\n\nURL: " + self.base_url)
        self.status_bar.config(text="✅ Settings saved")
    
    def on_user_name_changed(self, event):
        """Handle user name change"""
        self.user_name = self.user_name_var.get() or "User"
        self.save_personalization_settings()
        self.status_bar.config(text=f"👤 User name: {self.user_name}")
    
    def on_bot_name_changed(self, event):
        """Handle bot name change"""
        self.bot_name = self.bot_name_var.get() or "ChatBot"
        self.save_personalization_settings()
        self.status_bar.config(text=f"🤖 Bot name: {self.bot_name}")
    
    def on_personality_changed(self, event):
        """Handle personality change"""
        self.bot_personality = self.personality_var.get()
        self.system_prompt = self.personality_prompts.get(self.bot_personality, "You are a helpful AI assistant.")
        self.system_prompt_text.config(state=tk.NORMAL)
        self.system_prompt_text.delete("1.0", tk.END)
        self.system_prompt_text.insert(tk.END, self.system_prompt)
        self.save_personalization_settings()
        self.status_bar.config(text=f"✨ Personality: {self.bot_personality}")
    
    def update_system_prompt(self):
        """Update custom system prompt"""
        self.system_prompt = self.system_prompt_text.get("1.0", tk.END).strip()
        self.save_personalization_settings()
        self.status_bar.config(text="📝 System prompt updated")
    
    def load_personalization_settings(self):
        """Load personalization settings from file"""
        try:
            if os.path.exists("personalization.json"):
                with open("personalization.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user_name = data.get("user_name", "User")
                    self.bot_name = data.get("bot_name", "ChatBot")
                    self.bot_personality = data.get("bot_personality", "Friendly")
                    self.system_prompt = data.get("system_prompt", self.personality_prompts.get(self.bot_personality, "You are a helpful AI assistant."))
                    # Load API settings if saved
                    self.ollama_host = data.get("ollama_host", "localhost")
                    self.ollama_port = data.get("ollama_port", "11434")
                    self.base_url = f"http://{self.ollama_host}:{self.ollama_port}"
        except Exception as e:
            print(f"Error loading personalization: {e}")
    
    def save_personalization_settings(self):
        """Save personalization settings to file"""
        try:
            data = {
                "user_name": self.user_name,
                "bot_name": self.bot_name,
                "bot_personality": self.bot_personality,
                "system_prompt": self.system_prompt,
                "ollama_host": self.ollama_host,
                "ollama_port": self.ollama_port
            }
            with open("personalization.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving personalization: {e}")
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark_mode = not self.dark_mode
        self.set_theme(self.dark_mode)
        self.update_theme_colors()
        
        # Update colors for all widgets
        self.chat_display.config(bg=self.chat_bg, fg=self.chat_fg, insertbackground=self.chat_fg)
        self.input_field.config(bg=self.input_bg, fg=self.input_fg, insertbackground=self.input_fg)
        
        theme_name = "Dark" if self.dark_mode else "Light"
        self.status_bar.config(text=f"🌙 Theme changed to {theme_name}")
    
    def toggle_voice_input(self):
        """Toggle voice input recording"""
        try:
            import speech_recognition as sr
        except ImportError:
            messagebox.showerror("Error", "SpeechRecognition not installed. Install with: pip install SpeechRecognition")
            return
        
        if self.recording:
            self.recording = False
            self.voice_btn.config(text="🎤")
            self.status_bar.config(text="⏹️ Recording stopped")
            return
        
        self.recording = True
        self.voice_btn.config(text="⏹️")
        self.status_bar.config(text="🔴 Recording... (click 🎤 to stop)")
        
        def capture_voice():
            try:
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.status_bar.config(text="👂 Listening...")
                    audio = recognizer.listen(source, timeout=10)
                
                if not self.recording:  # User stopped recording
                    self.status_bar.config(text="Recording cancelled")
                    return
                
                self.status_bar.config(text="🔄 Processing audio...")
                text = recognizer.recognize_google(audio)
                
                # Insert into input field
                self.input_field.delete("1.0", tk.END)
                self.input_field.insert("1.0", text)
                self.input_field.config(fg=self.input_fg)
                self.status_bar.config(text="✅ Voice input received")
                self.recording = False
                self.voice_btn.config(text="🎤")
            except sr.UnknownValueError:
                messagebox.showwarning("Voice Input", "Could not understand audio. Please try again.")
                self.recording = False
                self.voice_btn.config(text="🎤")
                self.status_bar.config(text="❌ Could not understand audio")
            except sr.RequestError as e:
                messagebox.showerror("Voice Input", f"Error: {str(e)}")
                self.recording = False
                self.voice_btn.config(text="🎤")
                self.status_bar.config(text="❌ Voice input error")
        
        thread = threading.Thread(target=capture_voice, daemon=True)
        thread.start()
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = """
⌨️ KEYBOARD SHORTCUTS:

Ctrl + Enter    → Send message
Ctrl + S        → Save chat
Ctrl + O        → Load chat
Ctrl + F        → Search chat
Ctrl + E        → Export chat
Ctrl + T        → Toggle theme
Ctrl + H        → Show this help

🎤 Voice Button → Toggle voice input
📁 Upload       → Load file for analysis

Right-Click     → Copy message
Double-Click    → Select word
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def perform_search(self):
        """Search for text in chat"""
        search_term = self.search_var.get()
        if not search_term:
            return
        
        self.chat_display.tag_remove("highlight", "1.0", tk.END)
        
        start_pos = "1.0"
        while True:
            pos = self.chat_display.search(search_term, start_pos, nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(search_term)}c"
            self.chat_display.tag_add("highlight", pos, end_pos)
            start_pos = end_pos
        
        self.status_bar.config(text=f"🔍 Found search results")
    
    def clear_search(self):
        """Clear search highlighting"""
        self.chat_display.tag_remove("highlight", "1.0", tk.END)
        self.search_var.set("")
        self.status_bar.config(text="Search cleared")
    
    def show_search(self):
        """Activate search panel"""
        self.search_entry.focus()
    
    def export_chat(self):
        """Export chat to various formats"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("JSON files", "*.json"), ("HTML files", "*.html"), ("All files", "*.*")]
        )
        if not filename:
            return
        
        try:
            if filename.endswith('.json'):
                with open(filename, 'w') as f:
                    json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            elif filename.endswith('.md'):
                self._export_markdown(filename)
            elif filename.endswith('.html'):
                self._export_html(filename)
            else:  # .txt
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Chat History: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Bot: {self.bot_name} | User: {self.user_name}\n")
                    f.write("=" * 80 + "\n\n")
                    for msg in self.conversation_history:
                        role = self.user_name if msg["role"] == "user" else self.bot_name
                        f.write(f"{role}:\n{msg['content']}\n\n")
                        f.write("-" * 40 + "\n\n")
            
            messagebox.showinfo("Export", f"Chat exported to {filename.split(chr(92))[-1]}")
            self.status_bar.config(text="✅ Chat exported")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _export_markdown(self, filename):
        """Export chat as markdown"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Chat History\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
            f.write(f"**Bot**: {self.bot_name}  \n")
            f.write(f"**User**: {self.user_name}  \n")
            f.write(f"**Model**: {self.model}  \n\n")
            f.write("---\n\n")
            
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    f.write(f"### {self.user_name}\n\n{msg['content']}\n\n")
                else:
                    f.write(f"### {self.bot_name}\n\n{msg['content']}\n\n")
                f.write("---\n\n")
    
    def _export_html(self, filename):
        """Export chat as HTML"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chat History</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: #0a0e27; color: #00ffff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .message {{ margin-bottom: 15px; padding: 12px; border-radius: 8px; }}
        .user {{ background: #e8f5e9; border-left: 4px solid #4caf50; }}
        .bot {{ background: #e3f2fd; border-left: 4px solid #2196f3; }}
        .user-name {{ font-weight: bold; color: #2e7d32; }}
        .bot-name {{ font-weight: bold; color: #1565c0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>💬 Chat History</h1>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Bot:</strong> {self.bot_name} | <strong>User:</strong> {self.user_name} | <strong>Model:</strong> {self.model}</p>
    </div>
""")
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    f.write(f'<div class="message user"><span class="user-name">{self.user_name}:</span><br>{msg["content"]}</div>\n')
                else:
                    f.write(f'<div class="message bot"><span class="bot-name">{self.bot_name}:</span><br>{msg["content"]}</div>\n')
            f.write("</body>\n</html>")
    
    def save_chat(self):
        """Save chat to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.conversation_history, f, indent=2)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        for msg in self.conversation_history:
                            role = "User" if msg["role"] == "user" else "Bot"
                            f.write(f"{role}: {msg['content']}\n\n")
                messagebox.showinfo("Save", "Chat saved successfully!")
                self.status_bar.config(text="💾 Chat saved")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_chat(self):
        """Load chat from file"""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r') as f:
                        self.conversation_history = json.load(f)
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.delete("1.0", tk.END)
                    self.chat_display.config(state=tk.DISABLED)
                    for msg in self.conversation_history:
                        sender = "user" if msg["role"] == "user" else "bot"
                        self.add_message(msg["content"], sender)
                messagebox.showinfo("Load", "Chat loaded successfully!")
                self.status_bar.config(text="📂 Chat loaded")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def load_models(self):
        """Load available models in background"""
        def fetch_models():
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.available_models = [model["name"] for model in data.get("models", [])]
                    if self.available_models:
                        self.model_dropdown.config(values=self.available_models)
                        if self.model in self.available_models:
                            self.model_var.set(self.model)
                        else:
                            self.model_var.set(self.available_models[0])
                            self.model = self.available_models[0]
            except Exception as e:
                print(f"Error loading models: {e}")
        
        thread = threading.Thread(target=fetch_models, daemon=True)
        thread.start()
    
    def check_connection(self):
        """Check Ollama connection (initial)"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.status_label.config(text="🟢 Connected")
                return True
        except:
            pass
        
        self.status_label.config(text="🔴 Disconnected")
        return False
    
    def check_connection_async(self):
        """Check connection periodically in background"""
        def check_async():
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                is_connected = response.status_code == 200
            except:
                is_connected = False
            
            self.status_label.config(text="🟢 Connected" if is_connected else "🔴 Disconnected")
        
        thread = threading.Thread(target=check_async, daemon=True)
        thread.start()
        self.after(5000, self.check_connection_async)
    
    def send_message(self):
        """Send message to chatbot"""
        message = self.input_field.get("1.0", tk.END).strip()
        
        if not message or self.is_loading:
            return
        
        self.input_field.delete("1.0", tk.END)
        self.add_message(message, "user")
        self.is_loading = True
        self.send_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="⏳ Waiting for response...")
        
        self.add_message("...", "loading")
        
        thread = threading.Thread(target=self.get_response, args=(message,), daemon=True)
        thread.start()
    
    def stop_response_handler(self):
        """Stop the current response"""
        if self.is_loading:
            self.stop_response = True
            self.status_bar.config(text="⏹️ Stopping response...")
        else:
            messagebox.showinfo("Info", "No response is currently being generated")
    
    def get_response(self, user_message: str):
        """Get response from Ollama with streaming support"""
        try:
            self.stop_response = False  # Reset stop flag
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Translate to English if needed
            original_user_msg = user_message
            if self.current_language != "English":
                try:
                    translator = GoogleTranslator(source='auto', target='en')
                    user_message = translator.translate(user_message)
                except Exception as e:
                    print(f"Translation error: {e}")
            
            context = self.build_context()
            full_prompt = context + user_message
            
            # Remove loading message for streaming
            if self.streaming_var.get():
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete("end-2c", tk.END)
                self.chat_display.config(state=tk.DISABLED)
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": self.streaming_var.get(),
                "temperature": self.temperature,
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=300, stream=self.streaming_var.get())
            
            if response.status_code == 200:
                if self.streaming_var.get():
                    # Streaming response -> We buffer the response if non-English to translate whole sentences, or output directly
                    self.chat_display.config(state=tk.NORMAL)
                    full_response_en = ""
                    
                    if self.current_language == "English":
                        for line in response.iter_lines():
                            if self.stop_response:  # Check if stop was requested
                                self.status_bar.config(text="⏹️ Response stopped by user")
                                break
                            if line:
                                try:
                                    data = json.loads(line)
                                    chunk = data.get("response", "")
                                    full_response_en += chunk
                                    self.chat_display.insert(tk.END, chunk)
                                    self.chat_display.see(tk.END)
                                    self.chat_display.update()
                                except json.JSONDecodeError:
                                    pass
                    else:
                        # For other languages, we shouldn't stream character by character because translation needs context.
                        # We'll buffer the whole response, then translate it.
                        self.status_bar.config(text="🔄 Generating & Translating...")
                        self.chat_display.insert(tk.END, "Translating... ", "loading")
                        self.chat_display.update()
                        for line in response.iter_lines():
                            if self.stop_response:  # Check if stop was requested
                                self.status_bar.config(text="⏹️ Response stopped by user")
                                break
                            if line:
                                try:
                                    data = json.loads(line)
                                    chunk = data.get("response", "")
                                    full_response_en += chunk
                                except json.JSONDecodeError:
                                    pass
                                    
                        # Remove loading message
                        self.chat_display.delete("end-15c", tk.END)
                        
                        try:
                            # Lang code dictionary
                            lang_codes = {"Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn"}
                            dest_lang = lang_codes.get(self.current_language, "en")
                            translator = GoogleTranslator(source='en', target=dest_lang)
                            final_output = translator.translate(full_response_en)
                        except Exception as e:
                            print(f"Translation response error: {e}")
                            final_output = full_response_en
                            
                        self.chat_display.insert(tk.END, final_output)
                        self.chat_display.see(tk.END)
                        self.chat_display.update()

                    self.chat_display.insert(tk.END, "\n\n")
                    self.chat_display.config(state=tk.DISABLED)
                    
                    # Add label at beginning
                    self.chat_display.config(state=tk.NORMAL)
                    output_length = len(full_response_en) if self.current_language == "English" else len(final_output)
                    self.chat_display.insert("end-" + str(output_length + 2) + "c", f"{self.bot_name}: ", "bot")
                    self.chat_display.config(state=tk.DISABLED)
                else:
                    # Non-streaming response
                    data = response.json()
                    raw_response = data.get("response", "")
                    
                    final_output = raw_response
                    if self.current_language != "English":
                        try:
                            lang_codes = {"Hindi": "hi", "Tamil": "ta", "Telugu": "te", "Kannada": "kn"}
                            dest_lang = lang_codes.get(self.current_language, "en")
                            translator = GoogleTranslator(source='en', target=dest_lang)
                            final_output = translator.translate(raw_response)
                        except Exception as e:
                            print(f"Translation error: {e}")
                    
                    self.add_message(final_output, "bot")
                    full_response_en = raw_response
                
                # Store original English response in history for better multi-turn context
                if full_response_en:  
                    self.conversation_history.append({"role": "assistant", "content": full_response_en})
                if not self.stop_response:
                    self.status_bar.config(text="✅ Response received")
            else:
                self.add_message("Error: Could not get response from Ollama", "error")
                self.status_bar.config(text="❌ API Error")
        
        except requests.exceptions.ConnectionError:
            self.add_message("Error: Cannot connect to Ollama. Make sure it's running.", "error")
            self.status_bar.config(text="❌ Connection error")
        except Exception as e:
            self.add_message(f"Error: {str(e)}", "error")
            self.status_bar.config(text="❌ Error occurred")
        finally:
            self.is_loading = False
            self.send_btn.config(state=tk.NORMAL)
            self.stop_response = False  # Reset flag

    
    def build_context(self) -> str:
        """Build context from conversation history and file"""
        # Build with system prompt and personalization
        context = f"System: {self.system_prompt}\nUser name: {self.user_name}\nAssistant name: {self.bot_name}\n\n"
        
        # Add file content if loaded
        if self.current_file_content:
            context += f"=== FILE CONTEXT ===\nFile: {self.current_file_name}\nContent:\n{self.current_file_content}\n=== END FILE CONTEXT ===\n\n"
        
        if not self.conversation_history:
            return context
        
        # Add recent conversation history
        for msg in self.conversation_history[-5:]:
            role = self.user_name if msg["role"] == "user" else self.bot_name
            context += f"{role}: {msg['content']}\n\n"
        
        return context
    
    def clear_chat(self):
        """Clear chat display"""
        if messagebox.askyesno("Clear Chat", "Clear all messages?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.conversation_history = []
            self.add_message("👋 Chat cleared! How can I help you now?", "bot")
            self.status_bar.config(text="🗑️ Chat cleared")

if __name__ == "__main__":
    app = GUIChatbot()
    app.mainloop()
