from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, font
from .core import HangmanGame

class HangmanGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hangman Game")
        self.geometry("600x550")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        
        # Set style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                            font=('Arial', 24, 'bold'),
                            foreground='#2c3e50',
                            background='#f0f0f0')
        
        self.style.configure('Word.TLabel',
                            font=('Courier New', 28, 'bold'),
                            foreground='#2c3e50',
                            background='#f0f0f0')
        
        self.style.configure('Status.TLabel',
                            font=('Arial', 14),
                            foreground='#34495e',
                            background='#f0f0f0')
        
        self.style.configure('Wrong.TLabel',
                            font=('Arial', 12),
                            foreground='#e74c3c',
                            background='#f0f0f0')
        
        self.style.configure('Guess.TButton',
                            font=('Arial', 12, 'bold'),
                            foreground='white',
                            background='#3498db',
                            padding=(10, 5))
        
        self.style.map('Guess.TButton',
                      background=[('active', '#2980b9')])
        
        self.style.configure('Reset.TButton',
                            font=('Arial', 10),
                            foreground='white',
                            background='#7f8c8d',
                            padding=(5, 2))
        
        self.style.map('Reset.TButton',
                      background=[('active', '#95a5a6')])
        
        self.game = HangmanGame()
        self.create_widgets()
        self.update_view()

    def create_widgets(self):
        # Main container with padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        self.lbl_title = ttk.Label(main_frame, text="HANGMAN", style='Title.TLabel')
        self.lbl_title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Hangman drawing canvas
        self.canvas = tk.Canvas(main_frame, width=200, height=200, bg='white', relief='solid', bd=1)
        self.canvas.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Word display
        self.lbl_masked = ttk.Label(main_frame, style='Word.TLabel')
        self.lbl_masked.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        self.lbl_status = ttk.Label(status_frame, style='Status.TLabel')
        self.lbl_status.grid(row=0, column=0, padx=(0, 20))
        
        self.lbl_wrong = ttk.Label(status_frame, style='Wrong.TLabel')
        self.lbl_wrong.grid(row=0, column=1)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=4, column=0, columnspan=2, pady=(0, 20))
        
        ttk.Label(input_frame, text="Enter a letter:", style='Status.TLabel').grid(row=0, column=0, padx=(0, 10))
        
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(input_frame, width=5, font=('Arial', 16), textvariable=self.entry_var)
        self.entry.grid(row=0, column=1, padx=(0, 10))
        
        self.btn_guess = ttk.Button(input_frame, text="Guess", style='Guess.TButton', command=self.on_guess)
        self.btn_guess.grid(row=0, column=2)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2)
        
        self.btn_reset = ttk.Button(btn_frame, text="New Game", style='Reset.TButton', command=self.on_reset)
        self.btn_reset.grid(row=0, column=0, padx=(0, 10))
        
        self.btn_hint = ttk.Button(btn_frame, text="Hint", style='Reset.TButton', command=self.on_hint)
        self.btn_hint.grid(row=0, column=1)
        
        # Hint label
        self.lbl_hint = ttk.Label(main_frame, text="Type a letter (a-z) and press Guess or Enter", style='Status.TLabel')
        self.lbl_hint.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
        self.entry.focus_set()
        self.bind("<Return>", lambda _: self.on_guess())

    def draw_hangman(self):
        """Draw the hangman figure based on wrong guesses"""
        self.canvas.delete("all")
        
        # Draw gallows
        self.canvas.create_line(50, 180, 150, 180, width=3)  # base
        self.canvas.create_line(100, 180, 100, 50, width=3)  # pole
        self.canvas.create_line(100, 50, 150, 50, width=3)   # top
        self.canvas.create_line(150, 50, 150, 70, width=3)   # rope
        
        wrong_count = len(self.game.wrong_letters)
        
        if wrong_count >= 1:  # Head
            self.canvas.create_oval(140, 70, 160, 90, width=2)
        
        if wrong_count >= 2:  # Body
            self.canvas.create_line(150, 90, 150, 130, width=2)
        
        if wrong_count >= 3:  # Left arm
            self.canvas.create_line(150, 100, 130, 110, width=2)
        
        if wrong_count >= 4:  # Right arm
            self.canvas.create_line(150, 100, 170, 110, width=2)
        
        if wrong_count >= 5:  # Left leg
            self.canvas.create_line(150, 130, 130, 150, width=2)
        
        if wrong_count >= 6:  # Right leg
            self.canvas.create_line(150, 130, 170, 150, width=2)

    def on_guess(self):
        letter = self.entry_var.get().strip()
        self.entry_var.set("")
        
        if not letter:
            return
            
        ok, msg = self.game.guess(letter)
        self.update_view()
        
        if not ok and "already guessed" not in msg.lower() and "enter a single" not in msg.lower():
            self.bell()
            
        if self.game.is_over():
            if self.game.is_won():
                messagebox.showinfo("You won!", f"Great job! The word was: {self.game.reveal()}")
            else:
                messagebox.showerror("Game over", f"You lost. The word was: {self.game.reveal()}")

    def on_hint(self):
        # Reveal a random unguessed letter
        unguessed = [c for c in self.game.secret_word if c not in self.game.guessed_letters]
        if unguessed:
            hint = unguessed[0]
            messagebox.showinfo("Hint", f"Try the letter '{hint}'")
        else:
            messagebox.showinfo("Hint", "No hints needed! You've guessed all letters.")

    def on_reset(self):
        self.game.reset()
        self.update_view()

    def update_view(self):
        self.lbl_masked.config(text=self.game.masked_word())
        wrong = ", ".join(sorted(self.game.wrong_letters)) or "-"
        self.lbl_wrong.config(text=f"Wrong guesses: {wrong}")
        self.lbl_status.config(text=f"Lives left: {self.game.lives_left}")
        self.draw_hangman()

def run_gui():
    app = HangmanGUI()
    app.mainloop()