"""Beautiful Tkinter GUI to play against AI."""
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, font
    import random
except ImportError:
    tk = None
    print("Tkinter not available. GUI mode disabled.")

from .core import Hangman
from .ai_solver import AISolver

def run_gui():
    if tk is None:
        print("Tkinter not available")
        return

    # Create main window
    root = tk.Tk()
    root.title("Hangman AI Game")
    root.geometry("900x700")
    root.configure(bg="#2c3e50")
    root.resizable(False, False)
    
    # Set custom font
    try:
        custom_font = font.nametofont("TkDefaultFont")
        custom_font.configure(size=12)
        root.option_add("*Font", custom_font)
    except:
        pass
    
    # Colors
    bg_color = "#2c3e50"
    accent_color = "#3498db"
    secondary_color = "#9b59b6"
    text_color = "#ecf0f1"
    success_color = "#2ecc71"
    danger_color = "#e74c3c"
    warning_color = "#f39c12"
    
    # Style configuration
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure styles
    style.configure('TFrame', background=bg_color)
    style.configure('Header.TLabel', 
                   background=bg_color, 
                   foreground=text_color, 
                   font=('Helvetica', 24, 'bold'))
    style.configure('Word.TLabel', 
                   background=bg_color, 
                   foreground=text_color, 
                   font=('Courier', 28, 'bold'))
    style.configure('Info.TLabel', 
                   background=bg_color, 
                   foreground=text_color,
                   font=('Helvetica', 14))
    style.configure('Guess.TButton',
                   background=accent_color,
                   foreground=text_color,
                   font=('Helvetica', 12, 'bold'))
    style.configure('AI.TButton',
                   background=secondary_color,
                   foreground=text_color,
                   font=('Helvetica', 12, 'bold'))
    style.configure('New.TButton',
                   background=success_color,
                   foreground=text_color,
                   font=('Helvetica', 12, 'bold'))
    style.configure('TEntry',
                   fieldbackground=text_color,
                   foreground=bg_color,
                   font=('Helvetica', 14))
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20", style='TFrame')
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header
    header = ttk.Label(main_frame, 
                      text="🎮 HANGMAN AI GAME", 
                      style='Header.TLabel')
    header.pack(pady=10)
    
    # Hangman canvas
    canvas_frame = ttk.Frame(main_frame, style='TFrame')
    canvas_frame.pack(pady=20)
    
    canvas = tk.Canvas(canvas_frame, width=400, height=300, bg=bg_color, highlightthickness=0)
    canvas.pack()
    
    # Word display
    word_var = tk.StringVar()
    word_label = ttk.Label(main_frame, textvariable=word_var, style='Word.TLabel')
    word_label.pack(pady=20)
    
    # Info labels
    info_frame = ttk.Frame(main_frame, style='TFrame')
    info_frame.pack(pady=10)
    
    lives_var = tk.StringVar()
    lives_label = ttk.Label(info_frame, textvariable=lives_var, style='Info.TLabel')
    lives_label.pack(side=tk.LEFT, padx=20)
    
    guessed_var = tk.StringVar()
    guessed_label = ttk.Label(info_frame, textvariable=guessed_var, style='Info.TLabel')
    guessed_label.pack(side=tk.LEFT, padx=20)
    
    # Input frame
    input_frame = ttk.Frame(main_frame, style='TFrame')
    input_frame.pack(pady=20)
    
    ttk.Label(input_frame, text="Enter a letter:", style='Info.TLabel').pack()
    
    guess_var = tk.StringVar()
    guess_entry = ttk.Entry(input_frame, textvariable=guess_var, font=('Helvetica', 16), width=5, justify='center')
    guess_entry.pack(pady=10)
    
    # Buttons frame
    button_frame = ttk.Frame(main_frame, style='TFrame')
    button_frame.pack(pady=10)
    
    # Initialize game
    words = None
    game = Hangman(wordlist=words)
    ai = AISolver(game.wordlist)
    
    def draw_hangman():
        """Draw the hangman based on remaining lives."""
        canvas.delete("all")
        
        # Draw gallows
        canvas.create_line(100, 250, 300, 250, width=6, fill=text_color)  # base
        canvas.create_line(200, 250, 200, 50, width=6, fill=text_color)   # pole
        canvas.create_line(200, 50, 300, 50, width=6, fill=text_color)    # top
        canvas.create_line(300, 50, 300, 80, width=6, fill=text_color)    # rope
        
        lives_lost = game.max_lives - game.lives
        
        # Draw hangman parts based on lives lost
        if lives_lost >= 1:
            canvas.create_oval(275, 80, 325, 130, width=4, outline=danger_color)  # head
        if lives_lost >= 2:
            canvas.create_line(300, 130, 300, 190, width=4, fill=danger_color)  # body
        if lives_lost >= 3:
            canvas.create_line(300, 140, 270, 170, width=4, fill=danger_color)  # left arm
        if lives_lost >= 4:
            canvas.create_line(300, 140, 330, 170, width=4, fill=danger_color)  # right arm
        if lives_lost >= 5:
            canvas.create_line(300, 190, 270, 240, width=4, fill=danger_color)  # left leg
        if lives_lost >= 6:
            canvas.create_line(300, 190, 330, 240, width=4, fill=danger_color)  # right leg
        if lives_lost >= 7:
            canvas.create_oval(290, 95, 295, 100, fill=danger_color)  # left eye
            canvas.create_oval(305, 95, 310, 100, fill=danger_color)  # right eye
            canvas.create_arc(290, 110, 310, 120, start=0, extent=-180, outline=danger_color, width=3)  # sad mouth
    
    def update_display():
        """Update the game display."""
        word_var.set(game.pattern)
        lives_var.set(f"❤️ Lives: {game.lives}/{game.max_lives}")
        guessed_var.set(f"🔤 Guessed: {', '.join(sorted(game.guessed)) if game.guessed else 'None'}")
        draw_hangman()
        
        if game.is_finished():
            guess_entry.config(state='disabled')
            guess_btn.config(state='disabled')
            ai_btn.config(state='disabled')
            
            if game.is_won():
                messagebox.showinfo("Game Over", f"🎉 Congratulations! You won!\nThe word was: {game.secret.upper()}")
            else:
                messagebox.showinfo("Game Over", f"💀 Game Over! You lost.\nThe word was: {game.secret.upper()}")
    
    def make_guess():
        """Process a guess from the user."""
        ch = guess_var.get().strip().lower()
        if not ch or not ch.isalpha():
            messagebox.showerror("Invalid Input", "Please enter a valid letter!")
            return
            
        if ch in game.guessed:
            messagebox.showwarning("Already Guessed", f"You've already guessed '{ch}'!")
            return
            
        game.guess(ch)
        guess_var.set("")
        update_display()
    
    def ai_suggest():
        """Get a suggestion from the AI."""
        suggestion = ai.next_guess(game.visible_pattern())
        messagebox.showinfo("AI Suggestion", f"🤖 The AI suggests: {suggestion.upper()}")
    
    def new_game():
        """Start a new game."""
        nonlocal game, ai
        game = Hangman(wordlist=words)
        ai = AISolver(game.wordlist)
        guess_entry.config(state='normal')
        guess_btn.config(state='normal')
        ai_btn.config(state='normal')
        guess_var.set("")
        update_display()
    
    # Buttons
    guess_btn = ttk.Button(button_frame, text="🎯 Guess", command=make_guess, style='Guess.TButton')
    guess_btn.pack(side=tk.LEFT, padx=10)
    
    ai_btn = ttk.Button(button_frame, text="🤖 AI Suggest", command=ai_suggest, style='AI.TButton')
    ai_btn.pack(side=tk.LEFT, padx=10)
    
    new_btn = ttk.Button(button_frame, text="🔄 New Game", command=new_game, style='New.TButton')
    new_btn.pack(side=tk.LEFT, padx=10)
    
    # Bind Enter key to make guess
    guess_entry.bind('<Return>', lambda event: make_guess())
    
    # Focus on entry field
    guess_entry.focus()
    
    # Initial display
    update_display()
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Start the GUI
    root.mainloop()

if __name__ == '__main__':
    run_gui()