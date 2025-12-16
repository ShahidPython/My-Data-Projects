#!/usr/bin/env python3
"""
Advanced Binary Search Variants - Main Entry Point
"""
import sys
import time
import pyfiglet
from simple_chalk import chalk
from variants import cli, gui

def print_banner():
    """Display a stylish banner"""
    print("\n" + "="*60)
    ascii_banner = pyfiglet.figlet_format("Binary Search", font="small")
    print(chalk.blue(ascii_banner))
    print(chalk.green("      ADVANCED BINARY SEARCH VARIANTS"))
    print("="*60)
    print(chalk.yellow("  Efficient search algorithms at your fingertips"))
    print("="*60)

def print_menu():
    """Display the main menu with styling"""
    print(f"\n{chalk.cyan('╔══════════════════════════════════════════════════════╗')}")
    print(f"{chalk.cyan('║')}                  {chalk.bold('MAIN MENU')}                           {chalk.cyan('║')}")
    print(f"{chalk.cyan('╠══════════════════════════════════════════════════════╣')}")
    print(f"{chalk.cyan('║')}   {chalk.green('1.')} Command Line Interface (CLI)                    {chalk.cyan('║')}")
    print(f"{chalk.cyan('║')}   {chalk.green('2.')} Graphical User Interface (GUI)                  {chalk.cyan('║')}")
    print(f"{chalk.cyan('║')}   {chalk.green('3.')} Exit                                            {chalk.cyan('║')}")
    print(f"{chalk.cyan('╚══════════════════════════════════════════════════════╝')}")

def loading_animation():
    """Show a loading animation"""
    print(f"\n{chalk.yellow('Loading')}", end="", flush=True)
    for i in range(3):
        time.sleep(0.5)
        print(f"{chalk.yellow('.')}", end="", flush=True)
    print()

def main():
    """Main function with enhanced design"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input(f"\n{chalk.magenta('➤ Please enter your choice (1-3): ')}").strip()
            
            if choice == "1":
                loading_animation()
                cli.run_cli()
            elif choice == "2":
                loading_animation()
                gui.run_gui()
            elif choice == "3":
                print(f"\n{chalk.green('Thank you for using Advanced Binary Search!')}")
                print(f"{chalk.blue('Goodbye! 👋')}")
                sys.exit(0)
            else:
                print(f"\n{chalk.red('❌ Invalid choice. Please enter 1, 2, or 3.')}")
        except KeyboardInterrupt:
            print(f"\n\n{chalk.yellow('Operation cancelled by user. Exiting...')}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{chalk.red('❌ An error occurred:')} {e}")

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import pyfiglet
        import simple_chalk
    except ImportError:
        print("Please install required packages: pip install pyfiglet simple-chalk")
        sys.exit(1)
    
    main()