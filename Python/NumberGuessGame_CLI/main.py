import random

class MyNumberGame:
    def __init__(self):
        self.high_score = float('inf')  # Using float('inf') instead of None
        self.attempts = 0
        
    def show_intro(self):
        print("\n✨ Welcome to MY Number Guesser! ✨")
        print("--------------------------------")
        print("How to play:")
        print("- I'll pick a secret number")
        print("- You try to guess it")
        print("- Type 'stop' to quit early")
        print("- Beat your best score!\n")
    
    def pick_level(self):
        while True:
            print("Choose your challenge:")
            print("1) Simple (1-50)")
            print("2) Normal (1-100)")
            print("3) Tough (1-200)")
            level = input("Enter 1-3: ").strip()
            
            if level in ['1', '2', '3']:
                return level
            print("Oops! Just type 1, 2, or 3\n")

    def run_game(self, low, high, max_tries):
        secret = random.randint(low, high)
        self.attempts = 0
        
        print(f"\nI'm thinking of a number from {low} to {high}")
        print(f"You get {max_tries} guesses. Ready?\n")
        
        while self.attempts < max_tries:
            guess = input(f"Guess #{self.attempts + 1}: ").strip().lower()
            
            if guess == 'stop':
                print(f"\nGame stopped. The number was {secret}.")
                return False
            
            if not guess.isdigit():
                print("Please enter a number or 'stop'")
                continue
                
            self.attempts += 1
            num = int(guess)
            
            if num < secret:
                print("Go higher!")
            elif num > secret:
                print("Go lower!")
            else:
                print(f"\n✅ You got it in {self.attempts} tries!")
                if self.attempts < self.high_score:
                    self.high_score = self.attempts
                    print("🌟 New record!")
                return True
        
        print(f"\nOut of guesses! The number was {secret}.")
        return False

    def start(self):
        self.show_intro()
        
        while True:
            level = self.pick_level()
            
            if level == '1':
                result = self.run_game(1, 50, 8)  # Gives 8 tries for easy mode
            elif level == '2':
                result = self.run_game(1, 100, 6)
            else:
                result = self.run_game(1, 200, 4)
            
            print(f"\nYour best this session: {self.high_score} guesses")
            
            again = input("\nPlay again? (y/n): ").lower()
            while again not in ['y', 'n']:
                again = input("Just type y or n: ").lower()
            
            if again == 'n':
                print("\nThanks for playing my game! 👋")
                break

if __name__ == "__main__":
    game = MyNumberGame()
    game.start()