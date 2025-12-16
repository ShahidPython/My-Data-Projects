import argparse
import sys
from odd_even_checker.core import classify, check_range


def print_banner():
    """Print a stylish banner for the CLI."""
    banner = r"""
   ___  _  _   _   _      ___               _    _             
  / _ \| || | | | | |    / _ \_____ __ ___ | |__| | ___  _ __  
 | (_) | || |_| |_| |   | (_) |_  / '__/ _ \| '__| |/ _ \| '_ \ 
  \___/|_| \_|\___/     \___/ / /| | | (_) | |  | | (_) | | | |
      | _ \___ __ _ _ _| |_ /___|_|  \___/|_|  |_|\___/|_| |_|
     |   / -_) _` | ' \  _|                                   
     |_|_\___\__,_|_||_\__|                                   
    """
    print(banner)
    print("🔢 Odd or Even Checker - Command Line Interface")
    print("=" * 50)


def validate_number(input_str: str) -> int:
    """Validate and convert input string to integer.
    
    Args:
        input_str (str): Input string to validate
        
    Returns:
        int: Validated integer
        
    Raises:
        ValueError: If input cannot be converted to integer
    """
    try:
        return int(input_str)
    except ValueError:
        raise ValueError("❌ Invalid input. Please enter a valid integer.")


def interactive_mode():
    """Run the CLI in interactive mode."""
    while True:
        try:
            user_input = input("\nEnter a number (or 'quit' to exit, 'range' to check a range): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'range':
                range_mode()
                continue
                
            number = validate_number(user_input)
            result = classify(number)
            print(f"✅ {number} is {result}.")
            
        except ValueError as e:
            print(e)
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


def range_mode():
    """Check a range of numbers."""
    try:
        start = validate_number(input("Enter start number: "))
        end = validate_number(input("Enter end number: "))
        
        results = check_range(start, end)
        
        print(f"\n📊 Results for range {start} to {end}:")
        print("-" * 30)
        for num, classification in results.items():
            print(f"{num:>6} : {classification}")
            
    except ValueError as e:
        print(e)
    except KeyboardInterrupt:
        print("\nReturning to main menu...")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🔢 Odd or Even Checker (CLI) - Check if numbers are odd or even",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --number 42
  %(prog)s --range 1 10
  %(prog)s (for interactive mode)
        """
    )
    
    parser.add_argument(
        "-n", "--number",
        type=int,
        help="Check a specific number"
    )
    
    parser.add_argument(
        "-r", "--range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Check a range of numbers from START to END"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s v{__import__('odd_even_checker').__version__}"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.number is not None:
        # Single number mode
        try:
            result = classify(args.number)
            print(f"✅ {args.number} is {result}.")
        except TypeError as e:
            print(e)
            sys.exit(1)
            
    elif args.range:
        # Range mode
        try:
            start, end = args.range
            results = check_range(start, end)
            
            print(f"📊 Results for range {start} to {end}:")
            print("-" * 30)
            for num, classification in results.items():
                print(f"{num:>6} : {classification}")
                
        except TypeError as e:
            print(e)
            sys.exit(1)
            
    else:
        # Interactive mode
        print("💡 Tip: Use --help to see all options")
        interactive_mode()


if __name__ == "__main__":
    main()