"""
Palindrome Checker - Main Entry Point
"""
import sys
from cli import EnhancedPalindromeCLI, main as cli_main
from gui import main as gui_main

def display_menu():
    """Display the main menu with enhanced visual design"""
    print("\n" + "=" * 40)
    print("      PALINDROME CHECKER")
    print("=" * 40)
    print("1) CLI Interactive Mode")
    print("2) GUI Visual Mode")
    print("3) Quick Check (CLI)")
    print("0) Exit")
    print("=" * 40)

def main():
    """Main application entry point"""
    print("Welcome to Palindrome Checker!")
    
    while True:
        display_menu()
        choice = input("Select an option (0-3): ").strip()
        
        if choice == "1":
            # Create CLI instance and start interactive mode
            cli = EnhancedPalindromeCLI()
            cli.interactive_cli()
        elif choice == "2":
            gui_main()
        elif choice == "3":
            text = input("Enter text to check: ").strip()
            if text:
                # Create CLI instance and check text
                cli = EnhancedPalindromeCLI()
                cli.check_text_cli(text, show_explain=True)
            else:
                print("No text entered.")
        elif choice == "0":
            print("Thank you for using Palindrome Checker. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()