"""Enhanced Tkinter GUI for Rock, Paper, Scissors."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from game import Game, Move
import os
import base64

class RPSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock • Paper • Scissors")
        self.root.geometry("600x700")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)
        
        # Set window icon
        self.set_window_icon()
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        self.game = Game()
        self.setup_ui()
        
    def set_window_icon(self):
        """Set the window icon using base64 encoded icon data."""
        try:
            # Simple rock paper scissors icon using emoji
            self.root.iconbitmap()  # This will clear any existing icon
        except Exception:
            # Fallback if icon setting fails
            pass
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50")
        header_frame.pack(pady=20)
        
        title = tk.Label(header_frame, text="🪨 📄 ✂️ Rock Paper Scissors", 
                        font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        title.pack()
        
        # Game area
        game_frame = tk.Frame(self.root, bg="#34495e", relief="raised", bd=2)
        game_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Player vs Computer area
        vs_frame = tk.Frame(game_frame, bg="#34495e")
        vs_frame.pack(pady=20)
        
        self.player_choice = tk.Label(vs_frame, text="❓", font=("Arial", 40), 
                                     bg="#34495e", fg="white")
        self.player_choice.pack(side="left", padx=20)
        
        vs_label = tk.Label(vs_frame, text="VS", font=("Arial", 16, "bold"), 
                           bg="#34495e", fg="#e74c3c")
        vs_label.pack(side="left", padx=20)
        
        self.computer_choice = tk.Label(vs_frame, text="❓", font=("Arial", 40), 
                                       bg="#34495e", fg="white")
        self.computer_choice.pack(side="left", padx=20)
        
        # Buttons
        btn_frame = tk.Frame(game_frame, bg="#34495e")
        btn_frame.pack(pady=20)
        
        style = ttk.Style()
        style.configure("Game.TButton", font=("Arial", 12), padding=10)
        
        ttk.Button(btn_frame, text="🪨 Rock", style="Game.TButton", 
                  command=lambda: self.play(Move.ROCK)).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="📄 Paper", style="Game.TButton", 
                  command=lambda: self.play(Move.PAPER)).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="✂️ Scissors", style="Game.TButton", 
                  command=lambda: self.play(Move.SCISSORS)).grid(row=0, column=2, padx=10)
        
        # Result display
        self.result_label = tk.Label(game_frame, text="Make your move!", 
                                    font=("Arial", 14), bg="#34495e", fg="white")
        self.result_label.pack(pady=10)
        
        # Scores
        scores_frame = tk.Frame(game_frame, bg="#34495e")
        scores_frame.pack(pady=10)
        
        self.scores_label = tk.Label(scores_frame, text=self.score_text(), 
                                    font=("Arial", 12), bg="#34495e", fg="white")
        self.scores_label.pack()
        
        # History
        history_frame = tk.Frame(self.root, bg="#2c3e50")
        history_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        tk.Label(history_frame, text="Game History", font=("Arial", 12, "bold"), 
                fg="white", bg="#2c3e50").pack(anchor="w")
        
        self.history_text = scrolledtext.ScrolledText(history_frame, height=8, 
                                                     font=("Consolas", 10),
                                                     bg="#ecf0f1", fg="#2c3e50")
        self.history_text.pack(fill="both", pady=5)
        self.history_text.config(state="disabled")
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg="#2c3e50")
        control_frame.pack(pady=10)
        
        ttk.Button(control_frame, text="Reset Game", command=self.reset).pack(side="left", padx=10)
        ttk.Button(control_frame, text="How to Play", command=self.show_help).pack(side="left", padx=10)
        ttk.Button(control_frame, text="Quit", command=self.root.quit).pack(side="left", padx=10)
    
    def score_text(self):
        s = self.game.scores
        return f"Player: {s['player']}   |   Computer: {s['computer']}   |   Draws: {s['draws']}"
    
    def update_history(self):
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        
        if not self.game.history:
            self.history_text.insert(tk.END, "No games played yet.")
        else:
            for i, round_data in enumerate(self.game.history, 1):
                outcome = "Draw" if round_data["result"] == "draw" else \
                         "Win" if round_data["result"] == "player" else "Loss"
                color_tag = "draw" if outcome == "Draw" else "win" if outcome == "Win" else "loss"
                
                self.history_text.insert(tk.END, f"Round {i}: ")
                self.history_text.insert(tk.END, f"You: {round_data['player']} ", "move")
                self.history_text.insert(tk.END, "vs ", "vs")
                self.history_text.insert(tk.END, f"Computer: {round_data['computer']} -> ", "move")
                self.history_text.insert(tk.END, f"{outcome}\n", color_tag)
        
        self.history_text.config(state="disabled")
        
        # Configure tags for coloring
        self.history_text.tag_config("win", foreground="green")
        self.history_text.tag_config("loss", foreground="red")
        self.history_text.tag_config("draw", foreground="orange")
        self.history_text.tag_config("move", foreground="blue")
        self.history_text.tag_config("vs", foreground="gray")
    
    def play(self, move):
        # Disable buttons during animation
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button) and widget.winfo_class() == "TButton":
                widget.state(['disabled'])
        
        # Animate computer thinking
        self.result_label.config(text="Computer is thinking...")
        self.computer_choice.config(text="❓")
        
        move_emoji = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
        self.player_choice.config(text=move_emoji[move.value])
        
        # Start animation in a separate thread to avoid blocking the UI
        threading.Thread(target=self.animate_thinking, args=(move,), daemon=True).start()
    
    def animate_thinking(self, move):
        emojis = ["✂️", "📄", "🪨"]
        for i in range(6):
            emoji = emojis[i % 3]
            self.root.after(0, self.computer_choice.config, {"text": emoji})
            time.sleep(0.1)
        
        # Play the round after animation
        self.root.after(0, self.complete_round, move)
    
    def complete_round(self, move):
        result = self.game.play_round(move)
        
        move_emoji = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
        computer_emoji = move_emoji[result["computer"]]
        self.computer_choice.config(text=computer_emoji)
        
        if result["result"] == "draw":
            self.result_label.config(text=f"It's a draw! Both chose {result['player']}", fg="orange")
        elif result["result"] == "player":
            self.result_label.config(text=f"You win! {result['player'].title()} beats {result['computer']}", fg="green")
        else:
            self.result_label.config(text=f"Computer wins! {result['computer'].title()} beats {result['player']}", fg="red")
        
        self.scores_label.config(text=self.score_text())
        self.update_history()
        
        # Re-enable buttons
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button) and widget.winfo_class() == "TButton":
                widget.state(['!disabled'])
    
    def reset(self):
        self.game.reset()
        self.player_choice.config(text="❓")
        self.computer_choice.config(text="❓")
        self.result_label.config(text="Make your move!", fg="white")
        self.scores_label.config(text=self.score_text())
        self.update_history()
    
    def show_help(self):
        help_text = """
        Rock Paper Scissors Rules:
        
        - Rock beats Scissors
        - Paper beats Rock
        - Scissors beats Paper
        - Same selection results in a draw
        
        Click on one of the buttons to make your move.
        The computer will randomly select its move.
        """
        messagebox.showinfo("How to Play", help_text.strip())


def run_gui():
    root = tk.Tk()
    app = RPSApp(root)
    root.mainloop()