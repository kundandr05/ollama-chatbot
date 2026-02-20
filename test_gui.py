import tkinter as tk
from tkinter import ttk

# Test basic window
root = tk.Tk()
root.title("Test Window")
root.geometry("1100x800")

# Try to add some basic widgets
label = ttk.Label(root, text="Test Label")
label.pack(fill=tk.X, padx=20, pady=10)

button = ttk.Button(root, text="Test Button")
button.pack(fill=tk.X, padx=20, pady=10)

# Add a text widget
text = tk.Text(root, height=10)
text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

print("Window created successfully")
print(f"Window geometry: {root.geometry()}")
print("If you see this and the window appears, the basic GUI works")

root.mainloop()
