import tkinter as tk
from tkinter import ttk, messagebox
import time
from guessing_game.core import NumberGuessingGame, Difficulty, GameMode
from assets.styles import COLOR_PALETTE, FONTS

class NumberGuessingGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("500x600")
        self.root.configure(bg=COLOR_PALETTE["background"])
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Initialize game variables
        self.game = None
        self.start_time = None
        self.selected_difficulty = None
        self.difficulty_buttons = {}  # To store button references
        
        # Setup styles
        self.setup_styles()
        
        # Create main frames
        self.setup_welcome_frame()
        self.setup_game_frame()
        self.setup_result_frame()
        
        # Show welcome frame initially
        self.show_frame("welcome")
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"500x600+{x}+{y}")
    
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure("TFrame", background=COLOR_PALETTE["background"])
        style.configure("Title.TLabel", 
                        background=COLOR_PALETTE["background"],
                        foreground=COLOR_PALETTE["primary"],
                        font=FONTS["title"])
        style.configure("Subtitle.TLabel",
                        background=COLOR_PALETTE["background"],
                        foreground=COLOR_PALETTE["secondary"],
                        font=FONTS["subtitle"])
        style.configure("Primary.TButton",
                        background=COLOR_PALETTE["primary"],
                        foreground="white",
                        font=FONTS["button"],
                        padding=(20, 10))
        style.map("Primary.TButton",
                  background=[('active', COLOR_PALETTE["primary_dark"])])
        style.configure("Secondary.TButton",
                        background=COLOR_PALETTE["secondary"],
                        foreground="white",
                        font=FONTS["button"],
                        padding=(10, 5))
        style.configure("Game.TLabel",
                        background=COLOR_PALETTE["background"],
                        foreground=COLOR_PALETTE["text"],
                        font=FONTS["normal"])
        style.configure("Difficulty.TRadiobutton",
                        background=COLOR_PALETTE["background"],
                        foreground=COLOR_PALETTE["text"],
                        font=FONTS["normal"],
                        padding=(5, 2))
        style.map("Difficulty.TRadiobutton",
                  background=[('active', COLOR_PALETTE["primary_light"])],
                  foreground=[('active', 'white')])
    
    def setup_welcome_frame(self):
        """Create the welcome/start screen."""
        self.welcome_frame = ttk.Frame(self.root, style="TFrame")
        
        # Title
        title_label = ttk.Label(self.welcome_frame, 
                               text="Number Guessing Game", 
                               style="Title.TLabel")
        title_label.pack(pady=30)
        
        # Subtitle
        subtitle_label = ttk.Label(self.welcome_frame,
                                  text="Test your intuition and guessing skills!",
                                  style="Subtitle.TLabel")
        subtitle_label.pack(pady=10)
        
        # Difficulty selection
        difficulty_frame = ttk.Frame(self.welcome_frame, style="TFrame")
        difficulty_frame.pack(pady=20)
        
        ttk.Label(difficulty_frame, 
                 text="Select Difficulty:",
                 style="Game.TLabel").pack(pady=10)
        
        self.difficulty_var = tk.StringVar(value="")
        difficulties = [
            ("Easy (1-50, 10 attempts)", "easy"),
            ("Medium (1-100, 7 attempts)", "medium"), 
            ("Hard (1-200, 5 attempts)", "hard")
        ]
        
        # Create custom radiobuttons with better visual feedback
        for text, mode in difficulties:
            btn_frame = tk.Frame(difficulty_frame, bg=COLOR_PALETTE["background"], highlightthickness=1, 
                                highlightbackground=COLOR_PALETTE["primary_light"])
            btn_frame.pack(fill="x", padx=50, pady=5)
            
            # Create a custom radiobutton using a canvas for better visual feedback
            canvas = tk.Canvas(btn_frame, width=20, height=20, bg=COLOR_PALETTE["background"], 
                              highlightthickness=0)
            canvas.pack(side="left", padx=(10, 5))
            
            # Outer circle (always visible)
            canvas.create_oval(2, 2, 18, 18, outline=COLOR_PALETTE["primary"], width=1)
            
            # Inner circle (visible when selected)
            inner_circle = canvas.create_oval(6, 6, 14, 14, fill="", outline="")
            
            # Label
            label = tk.Label(btn_frame, text=text, bg=COLOR_PALETTE["background"], 
                           fg=COLOR_PALETTE["text"], font=FONTS["normal"], padx=10)
            label.pack(side="left", fill="x", expand=True)
            
            # Store references for updating later
            self.difficulty_buttons[mode] = {
                "canvas": canvas,
                "inner_circle": inner_circle,
                "label": label,
                "frame": btn_frame
            }
            
            # Bind click events
            for widget in [canvas, label, btn_frame]:
                widget.bind("<Button-1>", lambda e, m=mode: self.select_difficulty(m))
                widget.bind("<Enter>", lambda e, m=mode: self.hover_difficulty(m, True))
                widget.bind("<Leave>", lambda e, m=mode: self.hover_difficulty(m, False))
        
        # Selection indicator label
        self.selection_label = ttk.Label(self.welcome_frame, 
                                       text="Please select a difficulty level",
                                       style="Game.TLabel",
                                       foreground=COLOR_PALETTE["accent"])
        self.selection_label.pack(pady=10)
        
        # Start button
        self.start_button = ttk.Button(self.welcome_frame,
                                     text="Start Game",
                                     style="Primary.TButton",
                                     command=self.start_game,
                                     state="disabled")  # Initially disabled
        self.start_button.pack(pady=30)
    
    def select_difficulty(self, mode):
        """Handle difficulty selection with visual feedback."""
        self.selected_difficulty = mode
        self.difficulty_var.set(mode)
        
        # Update all buttons
        for m, btn_data in self.difficulty_buttons.items():
            if m == mode:
                # Selected button
                btn_data["canvas"].itemconfig(btn_data["inner_circle"], 
                                            fill=COLOR_PALETTE["primary"],
                                            outline=COLOR_PALETTE["primary"])
                btn_data["label"].config(fg=COLOR_PALETTE["primary"], font=("Arial", 12, "bold"))
                btn_data["frame"].config(highlightbackground=COLOR_PALETTE["primary"])
            else:
                # Deselected buttons
                btn_data["canvas"].itemconfig(btn_data["inner_circle"], 
                                            fill="", outline="")
                btn_data["label"].config(fg=COLOR_PALETTE["text"], font=FONTS["normal"])
                btn_data["frame"].config(highlightbackground=COLOR_PALETTE["primary_light"])
        
        # Update selection text
        difficulty_text = {
            "easy": "Easy difficulty selected",
            "medium": "Medium difficulty selected", 
            "hard": "Hard difficulty selected"
        }
        self.selection_label.config(text=difficulty_text.get(mode, "Difficulty selected"))
        
        # Enable start button
        self.start_button.config(state="normal")
    
    def hover_difficulty(self, mode, is_hovering):
        """Handle hover effects for difficulty options."""
        if self.selected_difficulty != mode:  # Only change if not selected
            if is_hovering:
                self.difficulty_buttons[mode]["label"].config(fg=COLOR_PALETTE["accent"])
                self.difficulty_buttons[mode]["frame"].config(highlightbackground=COLOR_PALETTE["accent"])
            else:
                self.difficulty_buttons[mode]["label"].config(fg=COLOR_PALETTE["text"])
                self.difficulty_buttons[mode]["frame"].config(
                    highlightbackground=COLOR_PALETTE["primary_light"])
    
    def setup_game_frame(self):
        """Create the game play screen."""
        self.game_frame = ttk.Frame(self.root, style="TFrame")
        
        # Game info
        self.range_label = ttk.Label(self.game_frame, 
                                    style="Game.TLabel")
        self.range_label.pack(pady=10)
        
        self.attempts_label = ttk.Label(self.game_frame,
                                       style="Game.TLabel")
        self.attempts_label.pack(pady=5)
        
        # Guess entry
        entry_frame = ttk.Frame(self.game_frame, style="TFrame")
        entry_frame.pack(pady=20)
        
        ttk.Label(entry_frame, 
                 text="Enter your guess:",
                 style="Game.TLabel").pack()
        
        self.guess_var = tk.StringVar()
        guess_entry = ttk.Entry(entry_frame,
                               textvariable=self.guess_var,
                               font=FONTS["normal"],
                               justify="center",
                               width=10)
        guess_entry.pack(pady=10)
        guess_entry.bind('<Return>', lambda e: self.check_guess())
        
        # Submit button
        submit_button = ttk.Button(entry_frame,
                                  text="Submit Guess",
                                  style="Secondary.TButton",
                                  command=self.check_guess)
        submit_button.pack(pady=10)
        
        # Feedback
        self.feedback_label = ttk.Label(self.game_frame,
                                       style="Game.TLabel",
                                       wraplength=400)
        self.feedback_label.pack(pady=20)
        
        # Guess history
        ttk.Label(self.game_frame,
                 text="Guess History:",
                 style="Game.TLabel").pack(pady=10)
        
        self.history_frame = ttk.Frame(self.game_frame, style="TFrame")
        self.history_frame.pack()
        
        # Hint button
        self.hint_button = ttk.Button(self.game_frame,
                                     text="Get Hint",
                                     style="Secondary.TButton",
                                     command=self.get_hint)
        self.hint_button.pack(pady=10)
        
        # Back button
        back_button = ttk.Button(self.game_frame,
                                text="Back to Menu",
                                style="Secondary.TButton",
                                command=lambda: self.show_frame("welcome"))
        back_button.pack(pady=10)
    
    def setup_result_frame(self):
        """Create the result screen."""
        self.result_frame = ttk.Frame(self.root, style="TFrame")
        
        self.result_label = ttk.Label(self.result_frame,
                                     style="Title.TLabel")
        self.result_label.pack(pady=30)
        
        self.stats_label = ttk.Label(self.result_frame,
                                    style="Game.TLabel")
        self.stats_label.pack(pady=10)
        
        button_frame = ttk.Frame(self.result_frame, style="TFrame")
        button_frame.pack(pady=30)
        
        ttk.Button(button_frame,
                  text="Play Again",
                  style="Primary.TButton",
                  command=self.play_again).pack(side="left", padx=10)
        
        ttk.Button(button_frame,
                  text="Main Menu",
                  style="Secondary.TButton",
                  command=lambda: self.show_frame("welcome")).pack(side="left", padx=10)
    
    def show_frame(self, frame_name):
        """Show the specified frame."""
        frames = {
            "welcome": self.welcome_frame,
            "game": self.game_frame,
            "result": self.result_frame
        }
        
        for frame in frames.values():
            frame.pack_forget()
        
        frames[frame_name].pack(fill="both", expand=True)
    
    def start_game(self):
        """Start a new game with selected difficulty."""
        if not self.selected_difficulty:
            messagebox.showwarning("Selection Required", "Please select a difficulty level first!")
            return
            
        difficulty_map = {
            "easy": Difficulty.EASY,
            "medium": Difficulty.MEDIUM,
            "hard": Difficulty.HARD
        }
        
        difficulty = difficulty_map[self.selected_difficulty]
        self.game = NumberGuessingGame(difficulty)
        
        # Update game UI
        self.range_label.config(text=f"I'm thinking of a number between {self.game.lower} and {self.game.upper}")
        self.attempts_label.config(text=f"Attempts remaining: {self.game.max_attempts}")
        self.guess_var.set("")
        self.feedback_label.config(text="")
        
        # Clear history
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        self.show_frame("game")
        self.start_time = time.time()
    
    def check_guess(self):
        """Check the user's guess."""
        try:
            guess = int(self.guess_var.get())
            result = self.game.guess(guess)
            
            # Check if guess is out of range (using the message content)
            if "out of range" in result["message"].lower():
                self.feedback_label.config(text=result["message"], foreground=COLOR_PALETTE["error"])
                return
            
            # Update attempts
            remaining_attempts = self.game.max_attempts - self.game.attempts
            self.attempts_label.config(text=f"Attempts remaining: {remaining_attempts}")
            
            # Add to history
            color = COLOR_PALETTE["success"] if result.get("win", False) else COLOR_PALETTE["text"]
            history_label = ttk.Label(self.history_frame,
                                     text=str(guess),
                                     foreground=color,
                                     font=FONTS["small"])
            history_label.pack(side="left", padx=5)
            
            if result.get("game_over", False):
                self.end_game(result)
            else:
                self.feedback_label.config(text=result["message"], foreground=COLOR_PALETTE["text"])
            
            self.guess_var.set("")
            
        except ValueError:
            self.feedback_label.config(text="Please enter a valid number", foreground=COLOR_PALETTE["error"])
    
    def get_hint(self):
        """Provide a hint to the player."""
        if self.game and not self.game.game_over:
            hint = self.game.get_hint()
            messagebox.showinfo("Hint", hint)
    
    def end_game(self, result):
        """End the game and show results."""
        end_time = time.time()
        time_taken = end_time - self.start_time
        
        if result.get("win", False):
            self.result_label.config(text="🎉 You Win! 🎉", foreground=COLOR_PALETTE["success"])
            self.stats_label.config(text=f"Number found in {result['attempts']} attempts!\nTime taken: {time_taken:.1f} seconds")
        else:
            self.result_label.config(text="Game Over", foreground=COLOR_PALETTE["error"])
            self.stats_label.config(text=f"The number was {self.game.secret_number}\nTime taken: {time_taken:.1f} seconds")
        
        self.show_frame("result")
    
    def play_again(self):
        """Start a new game with the same settings."""
        self.start_game()

def main():
    """Main GUI entry point."""
    root = tk.Tk()
    app = NumberGuessingGameGUI(root)
    root.mainloop()