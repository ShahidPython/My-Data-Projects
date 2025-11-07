import tkinter as tk
from tkinter import messagebox
import os
import math

# Create main window
window = tk.Tk()
window.title("Tic-Tac-Toe")
window.resizable(False, False)

# Set window icon
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
try:
    window.iconphoto(False, tk.PhotoImage(file=icon_path))
except Exception as e:
    print(f"Icon not loaded: {e}")

# Color scheme
DARK_PURPLE = "#4B0082"  # Dark purple cells
LIGHT_PURPLE = "#D8BFD8" # Light purple grid lines
X_COLOR = "#FF3333"      # Red color for X
X_GLOW = "#FF6666"       # Light red glow
O_COLOR = "#33B5FF"      # Blue color for O
O_GLOW = "#66CCFF"       # Sky blue glow
GLOW_LAYERS = 8          # Number of glow layers
GLOW_OFFSET = 2          # Glow spread amount
CELL_SIZE = 120          # Size of each cell

# Game variables
current_player = "X"
board = [["" for _ in range(3)] for _ in range(3)]
symbols = []  # Stores references to all drawn symbols

# Create canvas for drawing the board
canvas = tk.Canvas(window, width=CELL_SIZE*3+4, height=CELL_SIZE*3+4, 
                  bg=LIGHT_PURPLE, highlightthickness=0)
canvas.pack(pady=20)

# Draw the grid
for i in range(1, 3):
    # Vertical lines
    canvas.create_line(
        i*CELL_SIZE, 0,
        i*CELL_SIZE, CELL_SIZE*3,
        fill=LIGHT_PURPLE, width=2
    )
    # Horizontal lines
    canvas.create_line(
        0, i*CELL_SIZE,
        CELL_SIZE*3, i*CELL_SIZE,
        fill=LIGHT_PURPLE, width=2
    )

# Function to draw X with glow
def draw_x(canvas, x, y):
    size = CELL_SIZE // 3
    items = []
    
    # Create glow effect
    for i in range(GLOW_LAYERS, 0, -1):
        offset = i * GLOW_OFFSET / GLOW_LAYERS
        # Diagonal lines with glow
        items.append(canvas.create_line(
            x-size-offset, y-size-offset,
            x+size+offset, y+size+offset,
            fill=X_GLOW, width=8, tags="glow"
        ))
        items.append(canvas.create_line(
            x+size+offset, y-size-offset,
            x-size-offset, y+size+offset,
            fill=X_GLOW, width=8, tags="glow"
        ))
    
    # Main X symbol
    items.append(canvas.create_line(
        x-size, y-size,
        x+size, y+size,
        fill=X_COLOR, width=4, tags="symbol"
    ))
    items.append(canvas.create_line(
        x+size, y-size,
        x-size, y+size,
        fill=X_COLOR, width=4, tags="symbol"
    ))
    
    return items

# Function to draw O with glow
def draw_o(canvas, x, y):
    size = CELL_SIZE // 3
    items = []
    
    # Create glow effect
    for i in range(GLOW_LAYERS, 0, -1):
        offset = i * GLOW_OFFSET / GLOW_LAYERS
        items.append(canvas.create_oval(
            x-size-offset, y-size-offset,
            x+size+offset, y+size+offset,
            outline=O_GLOW, width=8, tags="glow"
        ))
    
    # Main O symbol
    items.append(canvas.create_oval(
        x-size, y-size,
        x+size, y+size,
        outline=O_COLOR, width=4, tags="symbol"
    ))
    
    return items

# Create dark purple cells
for i in range(3):
    for j in range(3):
        canvas.create_rectangle(
            j*CELL_SIZE, i*CELL_SIZE,
            (j+1)*CELL_SIZE, (i+1)*CELL_SIZE,
            fill=DARK_PURPLE, outline=LIGHT_PURPLE
        )

# Click handler
def on_click(event):
    global current_player
    col = event.x // CELL_SIZE
    row = event.y // CELL_SIZE
    
    if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == "":
        board[row][col] = current_player
        
        x_pos = col * CELL_SIZE + CELL_SIZE // 2
        y_pos = row * CELL_SIZE + CELL_SIZE // 2
        
        if current_player == "X":
            symbols.extend(draw_x(canvas, x_pos, y_pos))
        else:
            symbols.extend(draw_o(canvas, x_pos, y_pos))
        
        if check_winner():
            messagebox.showinfo("Game Over", f"Player {current_player} wins!")
            window.after(1000, reset_game)
        elif is_draw():
            messagebox.showinfo("Game Over", "It's a draw!")
            window.after(1000, reset_game)
        else:
            current_player = "O" if current_player == "X" else "X"

# Bind click event
canvas.bind("<Button-1>", on_click)

# Win check
def check_winner():
    # Check rows and columns
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "":
            return True
        if board[0][i] == board[1][i] == board[2][i] != "":
            return True
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != "":
        return True
    if board[0][2] == board[1][1] == board[2][0] != "":
        return True
    return False

# Draw check
def is_draw():
    for row in board:
        if "" in row:
            return False
    return True

# Reset game
def reset_game():
    global current_player, board, symbols
    current_player = "X"
    board = [["" for _ in range(3)] for _ in range(3)]
    canvas.delete("symbol")
    canvas.delete("glow")
    symbols = []

# Reset button
reset_btn = tk.Button(
    window,
    text="Reset",
    font=("Arial", 14),
    command=reset_game
)
reset_btn.pack(pady=10)

window.mainloop()