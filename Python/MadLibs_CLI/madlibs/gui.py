import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from .core import MadLibs
import random

def run_gui():
    root = tk.Tk()
    app = MadLibsGUI(root)
    root.mainloop()

class MadLibsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mad Libs Game")
        self.root.geometry("650x750")
        self.root.configure(bg="#f0f8ff")
        self.root.resizable(True, True)
        
        # Center the window on screen
        self.center_window()
        
        self.madlibs = MadLibs()
        self.current_template = None
        self.entries = {}
        
        self.setup_ui()
        self.new_story()
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_container, 
            text="Mad Libs", 
            font=("Comic Sans MS", 24, "bold"),
            fg="#ff6b6b",
            bg="#f0f8ff"
        )
        title_label.pack(pady=20)
        
        # Instructions
        instruction_label = tk.Label(
            main_container,
            text="Fill in the blanks below to create your own funny story!",
            font=("Arial", 12),
            fg="#333333",
            bg="#f0f8ff"
        )
        instruction_label.pack(pady=10)
        
        # Story title
        self.story_title = tk.Label(
            main_container,
            text="",
            font=("Arial", 14, "bold"),
            fg="#5d5d5d",
            bg="#f0f8ff"
        )
        self.story_title.pack(pady=5)
        
        # Input frame with scrollbar
        input_container = ttk.Frame(main_container)
        input_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a canvas and scrollbar for the input frame
        canvas = tk.Canvas(input_container, bg="#f0f8ff")
        scrollbar = ttk.Scrollbar(input_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=20)
        
        # Generate button
        generate_btn = ttk.Button(
            button_frame,
            text="Generate Story",
            command=self.generate_story
        )
        generate_btn.pack(side=tk.LEFT, padx=10)
        
        # New story button
        new_story_btn = ttk.Button(
            button_frame,
            text="New Story",
            command=self.new_story
        )
        new_story_btn.pack(side=tk.LEFT, padx=10)
        
        # Exit button
        exit_btn = ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit
        )
        exit_btn.pack(side=tk.LEFT, padx=10)
        
        # Story display
        story_frame = ttk.LabelFrame(main_container, text="Your Story")
        story_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.story_text = scrolledtext.ScrolledText(
            story_frame,
            wrap=tk.WORD,
            font=("Arial", 12),
            bg="#fffaf0",
            fg="#333333",
            padx=10,
            pady=10
        )
        self.story_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind mouse wheel to scrollbar
        self.story_text.bind("<MouseWheel>", self._on_mousewheel)
        canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        self.story_text.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def new_story(self):
        # Clear previous entries
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries = {}
        
        # Get a new template
        self.current_template = self.madlibs.get_random_template()
        template = self.current_template["template"]
        title = self.current_template.get("title", "Untitled Story")
        
        # Update story title
        self.story_title.config(text=title)
        
        # Get placeholders and create input fields
        placeholders = self.madlibs.get_placeholders(template)
        
        for i, placeholder in enumerate(placeholders):
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(
                frame, 
                text=f"{placeholder.capitalize()}:",
                width=15,
                anchor="e"
            )
            label.pack(side=tk.LEFT, padx=5)
            
            entry = ttk.Entry(frame, width=30, font=("Arial", 10))
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.entries[placeholder] = entry
            
            # Bind Enter key to generate story
            entry.bind("<Return>", lambda event: self.generate_story())
        
        # Clear story text
        self.story_text.delete(1.0, tk.END)
        
        # Focus on first entry
        if self.entries:
            first_entry = list(self.entries.values())[0]
            first_entry.focus()
    
    def generate_story(self):
        # Collect all inputs
        words = {}
        for placeholder, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showerror("Error", f"Please fill in the {placeholder} field!")
                entry.focus()
                return
            words[placeholder] = value
        
        try:
            # Generate the story
            story = self.madlibs.generate_story(self.current_template["template"], words)
            
            # Display the story
            self.story_text.delete(1.0, tk.END)
            self.story_text.insert(tk.END, story)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate story: {str(e)}")

if __name__ == "__main__":
    run_gui()