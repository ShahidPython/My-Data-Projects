
"""
Enhanced Tkinter GUI for Minesweeper with modern design and life system.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import threading
from pathlib import Path
from .core import Minesweeper, GameState
from .difficulty import ALL_DIFFICULTIES, create_custom_difficulty

# Sound support using tkinter's built-in capabilities
try:
    import winsound
    SOUND_WINDOWS = True
except ImportError:
    SOUND_WINDOWS = False

try:
    import os
    import subprocess
    SOUND_UNIX = True
except ImportError:
    SOUND_UNIX = False

class SoundManager:
    """Cross-platform sound manager."""
    
    def __init__(self):
        self.sounds = {}
        self.sound_enabled = False
        self._load_sounds()
    
    def _load_sounds(self):
        """Load sound files if available."""
        try:
            assets_path = Path(__file__).parent.parent / "assets"
            click_path = assets_path / "click.wav"
            explosion_path = assets_path / "explosion.wav"
            
            if click_path.exists():
                self.sounds['click'] = str(click_path)
                self.sound_enabled = True
            if explosion_path.exists():
                self.sounds['explosion'] = str(explosion_path)
                self.sound_enabled = True
        except Exception:
            pass
    
    def play(self, sound_name):
        """Play a sound effect."""
        if not self.sound_enabled or sound_name not in self.sounds:
            return
            
        sound_path = self.sounds[sound_name]
        
        try:
            if SOUND_WINDOWS:
                # Windows
                winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            elif SOUND_UNIX:
                # Unix/Linux/Mac - try different players
                for player in ['afplay', 'aplay', 'paplay', 'play']:
                    try:
                        subprocess.run([player, sound_path], 
                                     check=True, 
                                     capture_output=True, 
                                     timeout=1)
                        break
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                        continue
        except Exception:
            pass

class MinesweeperGUI:
    """Enhanced Tkinter GUI for Minesweeper."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.game = None
        self.buttons = []
        self.timer_running = False
        self.sound_manager = SoundManager()
        self.setup_window()
        
    def setup_window(self):
        """Setup the main window."""
        self.root.title("🎮 Minesweeper - Advanced Edition")
        self.root.configure(bg='#2c3e50')
        
        # Try to set window icon
        try:
            # Create a simple icon using tkinter
            self.root.iconbitmap(default=self._create_icon())
        except Exception:
            pass
        
        # Configure styles
        self.setup_styles()
        
        # Create menu
        self.create_menu()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info frame
        self.info_frame = ttk.Frame(self.main_frame, style='Info.TFrame')
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Game board frame
        self.board_frame = ttk.Frame(self.main_frame, style='Board.TFrame')
        self.board_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status frame
        self.status_frame = ttk.Frame(self.main_frame, style='Status.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.setup_info_widgets()
        self.setup_status_widgets()
        
        # Start with difficulty selection
        self.new_game()
        
    def _create_icon(self):
        """Create a simple icon for the window."""
        # This is a placeholder - in a real app you'd load an actual icon
        return None
        
    def setup_styles(self):
        """Setup custom styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Main.TFrame', background='#2c3e50')
        style.configure('Info.TFrame', background='#34495e', relief='raised')
        style.configure('Board.TFrame', background='#2c3e50')
        style.configure('Status.TFrame', background='#34495e', relief='raised')
        
        style.configure('Info.TLabel', background='#34495e', foreground='#ecf0f1', 
                       font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', background='#34495e', foreground='#ecf0f1', 
                       font=('Arial', 10))
        
        style.configure('Game.TButton', font=('Arial', 10, 'bold'))
        
    def create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root, bg='#34495e', fg='#ecf0f1')
        self.root.config(menu=menubar)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0, bg='#34495e', fg='#ecf0f1')
        menubar.add_cascade(label="🎮 Game", menu=game_menu)
        game_menu.add_command(label="🆕 New Game", command=self.new_game)
        game_menu.add_separator()
        game_menu.add_command(label="❌ Exit", command=self.root.quit)
        
        # Difficulty menu
        difficulty_menu = tk.Menu(menubar, tearoff=0, bg='#34495e', fg='#ecf0f1')
        menubar.add_cascade(label="⚙️ Difficulty", menu=difficulty_menu)
        
        for diff in ALL_DIFFICULTIES:
            difficulty_menu.add_command(
                label=f"{diff.name} ({diff.rows}x{diff.cols}, {diff.mines} mines, {diff.lives} lives)",
                command=lambda d=diff: self.start_game(d)
            )
        difficulty_menu.add_separator()
        difficulty_menu.add_command(label="🔧 Custom", command=self.custom_difficulty)
        
        # Sound menu
        sound_menu = tk.Menu(menubar, tearoff=0, bg='#34495e', fg='#ecf0f1')
        menubar.add_cascade(label="🔊 Sound", menu=sound_menu)
        sound_menu.add_command(label="🔊 Sound Enabled" if self.sound_manager.sound_enabled 
                              else "🔇 Sound Disabled", state='disabled')
        
    def setup_info_widgets(self):
        """Setup info display widgets."""
        # Time display
        self.time_label = ttk.Label(self.info_frame, text="⏱️ Time: 0s", style='Info.TLabel')
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        # Mines display
        self.mines_label = ttk.Label(self.info_frame, text="💣 Mines: 0", style='Info.TLabel')
        self.mines_label.pack(side=tk.LEFT, padx=10)
        
        # Lives display
        self.lives_label = ttk.Label(self.info_frame, text="❤️ Lives: 0", style='Info.TLabel')
        self.lives_label.pack(side=tk.LEFT, padx=10)
        
        # New game button
        self.new_game_btn = ttk.Button(self.info_frame, text="🆕 New Game", 
                                      command=self.new_game, style='Game.TButton')
        self.new_game_btn.pack(side=tk.RIGHT, padx=10)
        
    def setup_status_widgets(self):
        """Setup status display widgets."""
        self.status_label = ttk.Label(self.status_frame, text="🎮 Ready to play!", style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
    def new_game(self):
        """Start a new game with difficulty selection."""
        dialog = DifficultyDialog(self.root)
        if dialog.result:
            self.start_game(dialog.result)
            
    def custom_difficulty(self):
        """Create custom difficulty."""
        dialog = CustomDifficultyDialog(self.root)
        if dialog.result:
            self.start_game(dialog.result)
            
    def start_game(self, difficulty):
        """Start a new game with given difficulty."""
        self.game = Minesweeper(difficulty.rows, difficulty.cols, difficulty.mines, difficulty.lives)
        self.timer_running = True
        self.create_board()
        self.update_display()
        self.start_timer()
        
    def create_board(self):
        """Create the game board."""
        # Clear existing board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
            
        self.buttons = []
        
        # Calculate button size based on window size
        button_size = min(30, max(20, 600 // max(self.game.rows, self.game.cols)))
        
        for row in range(self.game.rows):
            button_row = []
            for col in range(self.game.cols):
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    width=2,
                    height=1,
                    font=('Arial', 8, 'bold'),
                    bg='#95a5a6',
                    fg='#2c3e50',
                    relief='raised',
                    bd=2,
                    command=lambda r=row, c=col: self.on_left_click(r, c)
                )
                btn.bind('<Button-3>', lambda e, r=row, c=col: self.on_right_click(r, c))
                btn.grid(row=row, column=col, padx=1, pady=1)
                button_row.append(btn)
            self.buttons.append(button_row)
            
    def on_left_click(self, row, col):
        """Handle left mouse click."""
        if self.game.state != GameState.PLAYING:
            return
            
        self.sound_manager.play('click')
        success = self.game.reveal_cell(row, col)
        
        if not success:  # Hit a mine
            self.sound_manager.play('explosion')
            if self.game.current_lives > 0:
                self.status_label.config(text=f"💥 Mine hit! Lives remaining: {self.game.current_lives}")
            else:
                self.timer_running = False
                self.status_label.config(text="💀 Game Over!")
                messagebox.showinfo("Game Over", "💥 You ran out of lives!")
                
        self.update_display()
        self.check_game_end()
        
    def on_right_click(self, row, col):
        """Handle right mouse click (flag toggle)."""
        if self.game.state != GameState.PLAYING:
            return
            
        self.game.toggle_flag(row, col)
        self.update_display()
        
    def update_display(self):
        """Update the display."""
        if not self.game:
            return
            
        # Update info labels
        self.time_label.config(text=f"⏱️ Time: {int(self.game.get_game_time())}s")
        self.mines_label.config(text=f"💣 Mines: {self.game.get_remaining_mines()}")
        
        if self.game.max_lives > 0:
            self.lives_label.config(text=f"❤️ Lives: {self.game.current_lives}")
        else:
            self.lives_label.config(text="💀 Hardcore Mode")
            
        # Update board
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                btn = self.buttons[row][col]
                
                if self.game.flagged[row][col]:
                    btn.config(text="🚩", bg='#e74c3c', state='normal')
                elif not self.game.revealed[row][col]:
                    btn.config(text="", bg='#95a5a6', state='normal')
                else:
                    btn.config(state='disabled')
                    if self.game.board[row][col]:
                        btn.config(text="💥", bg='#e74c3c')
                    else:
                        num = self.game.numbers[row][col]
                        if num == 0:
                            btn.config(text="", bg='#ecf0f1')
                        else:
                            colors = ['', '#3498db', '#27ae60', '#e74c3c', '#8e44ad', 
                                    '#d35400', '#f39c12', '#2c3e50', '#34495e']
                            btn.config(text=str(num), bg='#ecf0f1', 
                                     fg=colors[min(num, len(colors)-1)])
                                     
    def check_game_end(self):
        """Check if game has ended."""
        if self.game.state == GameState.WON:
            self.timer_running = False
            self.status_label.config(text="🎉 Congratulations! You won!")
            messagebox.showinfo("Victory!", f"🎉 You won in {int(self.game.get_game_time())} seconds!")
        elif self.game.state == GameState.LOST:
            self.timer_running = False
            
    def start_timer(self):
        """Start the game timer."""
        if self.timer_running and self.game:
            self.update_display()
            self.root.after(1000, self.start_timer)
            
    def run(self):
        """Run the GUI."""
        self.root.mainloop()

class DifficultyDialog:
    """Dialog for selecting game difficulty."""
    
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Difficulty")
        self.dialog.configure(bg='#2c3e50')
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets."""
        # Title
        title = tk.Label(self.dialog, text="🎮 Select Difficulty Level", 
                        font=('Arial', 16, 'bold'), bg='#2c3e50', fg='#ecf0f1')
        title.pack(pady=20)
        
        # Difficulty buttons
        for i, diff in enumerate(ALL_DIFFICULTIES):
            btn_text = f"{diff.name}\n{diff.rows}x{diff.cols}, {diff.mines} mines, {diff.lives} lives"
            btn = tk.Button(
                self.dialog,
                text=btn_text,
                font=('Arial', 10),
                bg='#3498db',
                fg='white',
                width=30,
                height=2,
                command=lambda d=diff: self.select_difficulty(d)
            )
            btn.pack(pady=5)
            
        # Custom button
        custom_btn = tk.Button(
            self.dialog,
            text="🔧 Custom Difficulty",
            font=('Arial', 10, 'bold'),
            bg='#e67e22',
            fg='white',
            width=30,
            height=2,
            command=self.custom_difficulty
        )
        custom_btn.pack(pady=10)
        
    def select_difficulty(self, difficulty):
        """Select a difficulty and close dialog."""
        self.result = difficulty
        self.dialog.destroy()
        
    def custom_difficulty(self):
        """Open custom difficulty dialog."""
        custom_dialog = CustomDifficultyDialog(self.dialog)
        if custom_dialog.result:
            self.result = custom_dialog.result
            self.dialog.destroy()

class CustomDifficultyDialog:
    """Dialog for creating custom difficulty."""
    
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Custom Difficulty")
        self.dialog.configure(bg='#2c3e50')
        self.dialog.geometry("350x250")
        self.dialog.resizable(False, False)
        
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets."""
        # Title
        title = tk.Label(self.dialog, text="🔧 Custom Difficulty", 
                        font=('Arial', 14, 'bold'), bg='#2c3e50', fg='#ecf0f1')
        title.pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.dialog, bg='#2c3e50')
        input_frame.pack(pady=10)
        
        # Rows input
        tk.Label(input_frame, text="Rows (5-30):", bg='#2c3e50', fg='#ecf0f1').grid(row=0, column=0, sticky='w', padx=5)
        self.rows_var = tk.StringVar(value="9")
        tk.Entry(input_frame, textvariable=self.rows_var, width=10).grid(row=0, column=1, padx=5)
        
        # Columns input
        tk.Label(input_frame, text="Columns (5-50):", bg='#2c3e50', fg='#ecf0f1').grid(row=1, column=0, sticky='w', padx=5)
        self.cols_var = tk.StringVar(value="9")
        tk.Entry(input_frame, textvariable=self.cols_var, width=10).grid(row=1, column=1, padx=5)
        
        # Mines input
        tk.Label(input_frame, text="Mines:", bg='#2c3e50', fg='#ecf0f1').grid(row=2, column=0, sticky='w', padx=5)
        self.mines_var = tk.StringVar(value="10")
        tk.Entry(input_frame, textvariable=self.mines_var, width=10).grid(row=2, column=1, padx=5)
        
        # Lives input
        tk.Label(input_frame, text="Lives (0=hardcore):", bg='#2c3e50', fg='#ecf0f1').grid(row=3, column=0, sticky='w', padx=5)
        self.lives_var = tk.StringVar(value="3")
        tk.Entry(input_frame, textvariable=self.lives_var, width=10).grid(row=3, column=1, padx=5)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, bg='#2c3e50')
        btn_frame.pack(pady=20)
        
        ok_btn = tk.Button(btn_frame, text="✅ OK", command=self.ok_clicked, 
                          bg='#27ae60', fg='white', width=10)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="❌ Cancel", command=self.dialog.destroy,
                              bg='#e74c3c', fg='white', width=10)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
    def ok_clicked(self):
        """Handle OK button click."""
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            mines = int(self.mines_var.get())
            lives = int(self.lives_var.get())
            
            if not (5 <= rows <= 30):
                raise ValueError("Rows must be between 5 and 30")
            if not (5 <= cols <= 50):
                raise ValueError("Columns must be between 5 and 50")
            if not (1 <= mines <= rows * cols - 9):
                raise ValueError(f"Mines must be between 1 and {rows * cols - 9}")
            if lives < 0:
                raise ValueError("Lives must be 0 or greater")
                
            self.result = create_custom_difficulty(rows, cols, mines, lives)
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

def main():
    """Main entry point for Tkinter GUI."""
    app = MinesweeperGUI()
    app.run()

if __name__ == "__main__":
    main()
