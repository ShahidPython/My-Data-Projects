
"""
Multiplayer Minesweeper mode for competitive play.
"""
import time
import random
import os
from typing import List, Dict, Optional
from .core import Minesweeper, GameState
from .difficulty import BEGINNER, INTERMEDIATE, EXPERT

class MultiplayerGame:
    """Multiplayer Minesweeper game manager."""
    
    def __init__(self, difficulty, num_players: int = 2):
        self.difficulty = difficulty
        self.num_players = num_players
        self.players = {}
        self.current_player = 0
        self.game_active = False
        
        # Create individual games for each player
        for i in range(num_players):
            player_name = f"Player {i + 1}"
            self.players[player_name] = {
                'game': Minesweeper(difficulty.rows, difficulty.cols, difficulty.mines, difficulty.lives),
                'score': 0,
                'time_penalty': 0.0,
                'status': 'waiting'
            }
            
    def get_current_player_name(self) -> str:
        """Get current player name."""
        return f"Player {self.current_player + 1}"
        
    def switch_player(self):
        """Switch to next player."""
        self.current_player = (self.current_player + 1) % self.num_players
        
    def make_move(self, player_name: str, row: int, col: int, action: str = 'reveal') -> bool:
        """Make a move for a player."""
        if player_name not in self.players:
            return False
            
        player = self.players[player_name]
        game = player['game']
        
        if action == 'reveal':
            success = game.reveal_cell(row, col)
            if success:
                # Award points for successful reveal
                if game.revealed[row][col] and not game.board[row][col]:
                    player['score'] += 1
            else:
                # Penalty for hitting mine
                player['time_penalty'] += 10.0
            return success
        elif action == 'flag':
            return game.toggle_flag(row, col)
            
        return False
        
    def get_leaderboard(self) -> List[Dict]:
        """Get current leaderboard."""
        leaderboard = []
        for name, player in self.players.items():
            game = player['game']
            total_time = game.get_game_time() + player['time_penalty']
            
            leaderboard.append({
                'name': name,
                'score': player['score'],
                'time': total_time,
                'state': game.state,
                'mines_remaining': game.get_remaining_mines(),
                'lives': player['game'].current_lives
            })
            
        # Sort by score (descending), then by time (ascending)
        leaderboard.sort(key=lambda x: (-x['score'], x['time']))
        return leaderboard
        
    def is_game_over(self) -> bool:
        """Check if multiplayer game is over."""
        finished_players = 0
        for player in self.players.values():
            if player['game'].state != GameState.PLAYING:
                finished_players += 1
                
        # Game over when all players finished or someone won
        return finished_players == self.num_players or any(
            p['game'].state == GameState.WON for p in self.players.values()
        )

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_multiplayer_banner():
    """Print multiplayer banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                   🎮 MULTIPLAYER MINESWEEPER 🎮               ║
    ║                     Competitive Edition                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print("\033[1;35m" + banner + "\033[0m")

def print_instructions():
    """Print detailed game instructions."""
    instructions = f"""
\033[1;32m┌─ 🎯 HOW TO PLAY MULTIPLAYER MINESWEEPER 🎯 ────────────────┐
│                                                             │
│ 🎮 GAME MODES:                                              │
│   • Turn-Based: Players take turns making moves            │
│   • Time Attack: Compete for highest score in time limit   │
│                                                             │
│ 🕹️  CONTROLS:                                               │
│   • r <row> <col>  - Reveal a cell                         │
│   • f <row> <col>  - Toggle flag on a cell                 │
│   • q              - Quit game                             │
│                                                             │
│ 📊 SCORING:                                                 │
│   • +1 point for each safe cell revealed                   │
│   • -10 seconds penalty for hitting mines (with lives)     │
│   • Win condition: Clear all non-mine cells                │
│                                                             │
│ 🏆 WINNING:                                                 │
│   • Turn-Based: First to win or highest score when done    │
│   • Time Attack: Highest score when time runs out          │
│                                                             │
│ 💡 TIPS:                                                    │
│   • Numbers show count of adjacent mines                   │
│   • Use flags to mark suspected mines                      │
│   • Start with corners and edges for better odds           │
│   • Think logically - use number clues!                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘\033[0m
"""
    print(instructions)

def print_player_board(game: Minesweeper, player_name: str):
    """Print a player's board."""
    print(f"\n\033[1;36m{player_name}'s Board:\033[0m")
    print("\033[1;33m   ", end="")
    
    # Column headers
    for col in range(min(game.cols, 20)):  # Limit display for readability
        print(f"{col:2}", end=" ")
    if game.cols > 20:
        print("...")
    else:
        print()
        
    # Board rows
    display_rows = min(game.rows, 15)  # Limit display for readability
    for row in range(display_rows):
        print(f"\033[1;33m{row:2}│\033[0m", end="")
        
        display_cols = min(game.cols, 20)
        for col in range(display_cols):
            cell_char = game.get_cell_display(row, col)
            if cell_char == ".":
                cell_char = "▓"
            elif cell_char == "F":
                cell_char = "\033[1;31m🚩\033[0m"
            elif cell_char == "*":
                cell_char = "\033[1;31m💥\033[0m"
            elif cell_char == " ":
                cell_char = "·"
            elif cell_char.isdigit():
                colors = ["\033[0m", "\033[1;34m", "\033[1;32m", "\033[1;31m", 
                         "\033[1;35m", "\033[1;33m", "\033[1;36m", "\033[1;37m"]
                num = int(cell_char)
                color = colors[min(num, len(colors)-1)]
                cell_char = f"{color}{cell_char}\033[0m"
                
            print(f"{cell_char:2} ", end="")
            
        if game.cols > 20:
            print("...")
        else:
            print()
            
    if game.rows > 15:
        print("   ...")

def print_leaderboard(leaderboard: List[Dict]):
    """Print the current leaderboard."""
    print("\n\033[1;32m🏆 LEADERBOARD 🏆\033[0m")
    print("\033[1;33m" + "─" * 60 + "\033[0m")
    
    for i, player in enumerate(leaderboard, 1):
        status_icon = "🎉" if player['state'] == GameState.WON else "💀" if player['state'] == GameState.LOST else "🎮"
        lives_text = f"❤️{player['lives']}" if player['lives'] > 0 else "💀"
        
        print(f"\033[1;37m{i}. {status_icon} {player['name']:<12} "
              f"Score: {player['score']:<3} Time: {player['time']:.1f}s "
              f"Mines: {player['mines_remaining']:<2} {lives_text}\033[0m")

def multiplayer_turn_based():
    """Play turn-based multiplayer."""
    clear_screen()
    print_multiplayer_banner()
    print_instructions()
    
    print("\n\033[1;34m🎮 Turn-Based Mode Setup\033[0m")
    
    # Setup
    difficulties = [BEGINNER, INTERMEDIATE, EXPERT]
    print("\nSelect difficulty:")
    for i, diff in enumerate(difficulties, 1):
        print(f"{i}. {diff.name} ({diff.rows}x{diff.cols}, {diff.mines} mines)")
        
    while True:
        try:
            choice = int(input("\nEnter choice (1-3): "))
            if 1 <= choice <= 3:
                difficulty = difficulties[choice - 1]
                break
            print("\033[1;31mInvalid choice!\033[0m")
        except ValueError:
            print("\033[1;31mPlease enter a number!\033[0m")
            
    while True:
        try:
            num_players = int(input("Number of players (2-4): "))
            if 2 <= num_players <= 4:
                break
            print("\033[1;31mMust be between 2 and 4 players!\033[0m")
        except ValueError:
            print("\033[1;31mPlease enter a number!\033[0m")
            
    # Create game
    mp_game = MultiplayerGame(difficulty, num_players)
    
    print(f"\n\033[1;32m🎮 Starting {difficulty.name} with {num_players} players!\033[0m")
    print("\033[1;33m📝 Remember the commands: r <row> <col> (reveal), f <row> <col> (flag), q (quit)\033[0m")
    input("\n\033[1;36mPress Enter when all players are ready...\033[0m")
    
    # Game loop
    while not mp_game.is_game_over():
        current_player = mp_game.get_current_player_name()
        current_game = mp_game.players[current_player]['game']
        
        # Skip if player is done
        if current_game.state != GameState.PLAYING:
            mp_game.switch_player()
            continue
            
        # Display current state
        clear_screen()
        print_multiplayer_banner()
        print_leaderboard(mp_game.get_leaderboard())
        print_player_board(current_game, current_player)
        
        # Game info
        print(f"\n\033[1;35m🎯 {current_player}'s Turn\033[0m")
        print(f"⏱️ Time: {int(current_game.get_game_time())}s | "
              f"💣 Mines: {current_game.get_remaining_mines()} | "
              f"❤️ Lives: {current_game.current_lives} | "
              f"🎯 Score: {mp_game.players[current_player]['score']}")
              
        # Show command reminder
        print(f"\n\033[1;33m💡 Commands: r <row> <col> (reveal), f <row> <col> (flag), q (quit)\033[0m")
        
        # Get player input
        try:
            command = input(f"\n\033[1;32m{current_player}, enter command: \033[0m").strip().lower()
            
            if command == 'q':
                break
                
            parts = command.split()
            if len(parts) == 3:
                action, row_str, col_str = parts
                try:
                    row, col = int(row_str), int(col_str)
                    
                    if action == 'r':
                        success = mp_game.make_move(current_player, row, col, 'reveal')
                        if not success and current_game.current_lives > 0:
                            print(f"\n\033[1;31m💥 {current_player} hit a mine! Lives: {current_game.current_lives}\033[0m")
                            input("\033[1;33mPress Enter to continue...\033[0m")
                    elif action == 'f':
                        mp_game.make_move(current_player, row, col, 'flag')
                    else:
                        print("\033[1;31mInvalid action! Use 'r' for reveal or 'f' for flag.\033[0m")
                        input("\033[1;33mPress Enter to continue...\033[0m")
                        continue
                        
                except ValueError:
                    print("\033[1;31mInvalid coordinates! Use numbers only.\033[0m")
                    input("\033[1;33mPress Enter to continue...\033[0m")
                    continue
            else:
                print("\033[1;31mInvalid command! Use: r <row> <col> or f <row> <col>\033[0m")
                input("\033[1;33mPress Enter to continue...\033[0m")
                continue
                
        except KeyboardInterrupt:
            print("\n\033[1;33mGame interrupted!\033[0m")
            break
            
        # Switch to next player
        mp_game.switch_player()
        
    # Final results
    clear_screen()
    print_multiplayer_banner()
    print("\n\033[1;32m🎊 FINAL RESULTS 🎊\033[0m")
    print_leaderboard(mp_game.get_leaderboard())
    
    # Announce winner
    leaderboard = mp_game.get_leaderboard()
    winner = leaderboard[0]
    if winner['state'] == GameState.WON:
        print(f"\n\033[1;33m🏆 {winner['name']} WINS! 🏆\033[0m")
        print(f"\033[1;32mCongratulations on completing the minefield!\033[0m")
    else:
        print(f"\n\033[1;36m🥇 {winner['name']} leads with {winner['score']} points!\033[0m")
        
    input("\n\033[1;32mPress Enter to return to main menu...\033[0m")

def multiplayer_time_attack():
    """Play time attack multiplayer."""
    clear_screen()
    print_multiplayer_banner()
    print_instructions()
    
    print("\n\033[1;31m⚡ Time Attack Mode Setup\033[0m")
    print("All players compete simultaneously for the highest score!")
    
    # Setup
    difficulties = [BEGINNER, INTERMEDIATE, EXPERT]
    print("\nSelect difficulty:")
    for i, diff in enumerate(difficulties, 1):
        print(f"{i}. {diff.name}")
        
    while True:
        try:
            choice = int(input("\nEnter choice (1-3): "))
            if 1 <= choice <= 3:
                difficulty = difficulties[choice - 1]
                break
            print("\033[1;31mInvalid choice!\033[0m")
        except ValueError:
            print("\033[1;31mPlease enter a number!\033[0m")
            
    # Create games for each player
    print("\n⚡ 2-minute time attack starting...")
    print("Players will compete for the highest score!")
    input("\n\033[1;36mPress Enter when ready...\033[0m")
    
    # Simulate concurrent play (simplified for CLI)
    mp_game = MultiplayerGame(difficulty, 2)
    start_time = time.time()
    game_duration = 120  # 2 minutes
    
    player_scores = {"Player 1": 0, "Player 2": 0}
    
    print(f"\n\033[1;32m⚡ TIME ATTACK STARTED! ⚡\033[0m")
    print("Simulating 2-minute competitive session...")
    print("\033[1;33m(In a real game, players would play on separate devices)\033[0m")
    
    # Simulate gameplay
    while time.time() - start_time < game_duration:
        for player_name in mp_game.players:
            game = mp_game.players[player_name]['game']
            if game.state == GameState.PLAYING:
                # Simulate random moves
                row = random.randint(0, game.rows - 1)
                col = random.randint(0, game.cols - 1)
                if not game.revealed[row][col] and not game.flagged[row][col]:
                    success = mp_game.make_move(player_name, row, col, 'reveal')
                    if success:
                        player_scores[player_name] += 1
                        
        time.sleep(0.1)  # Small delay
        
        # Show progress
        elapsed = time.time() - start_time
        remaining = max(0, game_duration - elapsed)
        print(f"\r⏱️ Time remaining: {remaining:.1f}s | "
              f"Player 1: {player_scores['Player 1']} | "
              f"Player 2: {player_scores['Player 2']}", end="")
              
    print("\n\n\033[1;32m🏁 TIME'S UP! 🏁\033[0m")
    
    # Final results
    leaderboard = mp_game.get_leaderboard()
    print_leaderboard(leaderboard)
    
    winner = max(player_scores, key=player_scores.get)
    print(f"\n\033[1;33m🏆 {winner} WINS with {player_scores[winner]} points! 🏆\033[0m")
    
    input("\n\033[1;32mPress Enter to return to main menu...\033[0m")

def main():
    """Main multiplayer entry point."""
    while True:
        clear_screen()
        print_multiplayer_banner()
        
        print("\n\033[1;33mSelect Multiplayer Mode:\033[0m")
        print("1. 🎯 Turn-Based (2-4 players take turns)")
        print("2. ⚡ Time Attack (Competitive scoring)")
        print("3. 📖 View Instructions")
        print("4. 🔙 Back to Main Menu")
        
        choice = input("\n\033[1;32mEnter choice (1-4): \033[0m").strip()
        
        if choice == "1":
            multiplayer_turn_based()
        elif choice == "2":
            multiplayer_time_attack()
        elif choice == "3":
            clear_screen()
            print_multiplayer_banner()
            print_instructions()
            input("\n\033[1;36mPress Enter to return to multiplayer menu...\033[0m")
        elif choice == "4":
            break
        else:
            print("\033[1;31mInvalid choice!\033[0m")
            input("\033[1;33mPress Enter to continue...\033[0m")

if __name__ == "__main__":
    main()
