import random
import time
from colorama import Fore, init

# Initialize colorama for colored text
init(autoreset=True)

# Color mapping for each face (1-6)
DOT_COLORS = {
    1: Fore.RED,      # 1 dot = red
    2: Fore.BLUE,     # 2 dots = blue
    3: Fore.YELLOW,   # 3 dots = yellow
    4: Fore.GREEN,    # 4 dots = green
    5: Fore.MAGENTA,  # 5 dots = magenta (closest to orange)
    6: Fore.WHITE     # 6 dots = white (since brown isn't available)
}

# ASCII dice template (white)
DICE_TEMPLATE = """
    ┌───────┐
    │ {0} │
    │ {1} │
    │ {2} │
    └───────┘
"""

# Dot positions for each face
DOT_LAYOUT = {
    1: ["     ", "  ●  ", "     "],
    2: ["●    ", "     ", "    ●"],
    3: ["●    ", "  ●  ", "    ●"],
    4: ["●   ●", "     ", "●   ●"],
    5: ["●   ●", "  ●  ", "●   ●"],
    6: ["●   ●", "●   ●", "●   ●"]
}

def colored_dice(roll):
    """Return colored ASCII dice art"""
    color = DOT_COLORS[roll]
    rows = DOT_LAYOUT[roll]
    # Apply color to each row of dots
    colored_rows = [color + row + Fore.RESET for row in rows]
    return DICE_TEMPLATE.format(*colored_rows)

def main():
    print(Fore.WHITE + "🎲 DICE ROLLER 🎲")
    print("Press ENTER to roll, 'q' to quit\n")
    
    while True:
        user_input = input("> ").strip().lower()
        
        if user_input == 'q':
            print("Thanks for playing! 👋")
            break
        
        print("\nRolling the dice...")
        time.sleep(0.8)  # Dramatic pause
        
        roll = random.randint(1, 6)
        print(colored_dice(roll))
        print(f"→ You rolled a {roll}!\n")

if __name__ == "__main__":
    main()