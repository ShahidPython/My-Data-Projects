"""
Modern Command-line interface for palindrome checker with rich visuals
"""
import sys
import argparse
from enum import Enum
from core import is_palindrome, explain

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.box import ROUNDED
    from rich import print as rprint
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class MessageType(Enum):
    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    INFO = "blue"
    DEFAULT = "white"

class EnhancedPalindromeCLI:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.history = []
        
    def print_message(self, message, msg_type=MessageType.DEFAULT, style="bold"):
        """Print styled message with rich or fallback to basic colors"""
        if self.console:
            self.console.print(f"[{msg_type.value} {style}]{message}[/]")
        else:
            # Fallback to basic ANSI colors
            color_codes = {
                MessageType.SUCCESS: "\033[92m",
                MessageType.ERROR: "\033[91m",
                MessageType.WARNING: "\033[93m",
                MessageType.INFO: "\033[94m",
                MessageType.DEFAULT: "\033[0m"
            }
            print(f"{color_codes[msg_type]}{message}\033[0m")
    
    def print_panel(self, title, content, border_style="blue"):
        """Print content in a styled panel"""
        if self.console:
            panel = Panel(
                content,
                title=title,
                title_align="left",
                border_style=border_style,
                box=ROUNDED,
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print(f"\n{title}")
            print("=" * len(title))
            print(content)
            print()
    
    def create_result_table(self, text, result):
        """Create a rich table for results"""
        if not self.console:
            return None
            
        table = Table(show_header=False, box=ROUNDED, show_lines=True)
        table.add_column("Property", style="cyan", width=15)
        table.add_column("Value", style="white")
        
        info = explain(text, find_substrings=True)
        
        table.add_row("Input", f'[bold]"{text}"[/]')
        table.add_row("Result", 
                     "[bold green]PALINDROME ✓[/]" if result else "[bold red]NOT A PALINDROME ✗[/]")
        table.add_row("Normalized", f'"{info.normalized}"')
        table.add_row("Length", f"{info.length} characters")
        table.add_row("Reversed", f'"{info.reversed}"')
        
        return table
    
    def show_substrings(self, substrings):
        """Display palindromic substrings in a table"""
        if not substrings:
            return
            
        if self.console:
            table = Table(title="Palindromic Substrings", box=ROUNDED)
            table.add_column("Substring", style="green")
            table.add_column("Position", style="cyan")
            table.add_column("Length", style="yellow", justify="right")
            
            for start, end, substring in substrings[:8]:
                table.add_row(f'"{substring}"', f"{start}-{end-1}", str(len(substring)))
            
            self.console.print(table)
        else:
            print("\nPalindromic Substrings:")
            for start, end, substring in substrings[:8]:
                print(f"  '{substring}' (positions {start}-{end-1}, length: {len(substring)})")
    
    def check_text_cli(self, text, show_explain=False, find_substrings=False):
        """
        Check text and display results with enhanced visuals
        """
        # Show progress spinner for effect
        if self.console and show_explain:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Analyzing text...", total=None)
                result = is_palindrome(text)
                info = explain(text, find_substrings=find_substrings)
        else:
            result = is_palindrome(text)
            info = explain(text, find_substrings=find_substrings)
        
        # Display main result
        if self.console:
            self.print_panel(
                "Palindrome Analysis Result", 
                self.create_result_table(text, result),
                "green" if result else "red"
            )
        else:
            print("\n" + "=" * 60)
            print("Palindrome Check Result")
            print("=" * 60)
            print(f"Text: '{text}'")
            print("✓ PALINDROME" if result else "✗ NOT A PALINDROME")
        
        # Show detailed analysis if requested
        if show_explain:
            if self.console:
                explanation = Text()
                if info.is_palindrome:
                    explanation.append("✓ The normalized text reads the same forwards and backwards\n", style="bold green")
                else:
                    explanation.append("✗ The normalized text does not read the same forwards and backwards\n", style="bold red")
                
                self.print_panel("Detailed Analysis", explanation)
                
                if info.substrings and find_substrings:
                    self.show_substrings(info.substrings)
            else:
                print(f"\nDetailed Analysis:")
                print(f"Normalized: '{info.normalized}'")
                print(f"Length: {info.length} characters")
                print(f"Reversed: '{info.reversed}'")
                
                if info.is_palindrome:
                    print("✓ The normalized text reads the same forwards and backwards")
                else:
                    print("✗ The normalized text does not read the same forwards and backwards")
                    
                if info.substrings and find_substrings:
                    print(f"\nPalindromic Substrings Found:")
                    for start, end, substring in info.substrings[:5]:
                        print(f"  '{substring}' (positions {start}-{end-1})")
                    if len(info.substrings) > 5:
                        print(f"  ... and {len(info.substrings) - 5} more")
    
    def display_help(self):
        """Show enhanced help information"""
        if self.console:
            help_text = Text()
            help_text.append("Available commands:\n", style="bold underline")
            help_text.append("  <text>          - Check if text is a palindrome\n", style="green")
            help_text.append("  detail <text>   - Detailed analysis with substring search\n", style="cyan")
            help_text.append("  explain <text>  - Detailed analysis without substring search\n", style="blue")
            help_text.append("  history         - Show check history\n", style="yellow")
            help_text.append("  clear           - Clear history\n", style="magenta")
            help_text.append("  help, ?         - Show this help\n", style="white")
            help_text.append("  quit, exit, q   - Exit interactive mode\n", style="red")
            
            self.print_panel("Interactive Mode Help", help_text, "cyan")
        else:
            print("Available commands:")
            print("  <text>          - Check if text is a palindrome")
            print("  detail <text>   - Detailed analysis with substring search")
            print("  explain <text>  - Detailed analysis without substring search")
            print("  history         - Show check history")
            print("  clear           - Clear history")
            print("  help, ?         - Show this help")
            print("  quit, exit, q   - Exit interactive mode")
    
    def show_history(self):
        """Display check history in a formatted table"""
        if not self.history:
            self.print_message("No history yet.", MessageType.INFO)
            return
            
        if self.console:
            table = Table(title="Check History", box=ROUNDED)
            table.add_column("#", style="dim", width=4)
            table.add_column("Text", style="green")
            table.add_column("Result", style="cyan")
            table.add_column("Normalized", style="yellow")
            
            for i, (text, result, normalized) in enumerate(reversed(self.history[-10:]), 1):
                status = "✓" if result else "✗"
                color = "green" if result else "red"
                # Truncate long text for display
                display_text = text if len(text) <= 30 else text[:27] + "..."
                table.add_row(
                    str(i), 
                    display_text, 
                    f"[{color}]{status}[/]", 
                    normalized if len(normalized) <= 20 else normalized[:17] + "..."
                )
            
            self.console.print(table)
        else:
            print("Check history:")
            for i, (text, result, normalized) in enumerate(reversed(self.history[-10:]), 1):
                status = "✓" if result else "✗"
                print(f"  {i:2d}. {status} '{text}' → '{normalized}'")
    
    def interactive_cli(self):
        """Enhanced interactive CLI mode with rich interface"""
        if self.console:
            self.print_panel(
                "Interactive Palindrome Checker", 
                "Enter text to check, or type 'help' for available commands\nType 'quit' to exit", 
                "blue"
            )
        else:
            print("\nInteractive Palindrome Checker")
            print("Enter text to check, or type 'help' for available commands")
            print("Type 'quit' to exit")
            print("-" * 50)
        
        while True:
            try:
                if self.console:
                    user_input = Prompt.ask("[bold yellow]>>[/]").strip()
                else:
                    user_input = input(">> ").strip()
            except (EOFError, KeyboardInterrupt):
                self.print_message("\nExiting interactive mode.", MessageType.INFO)
                break
                
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                self.print_message("Exiting interactive mode.", MessageType.INFO)
                break
                
            if user_input.lower() in ['help', '?']:
                self.display_help()
                continue
                
            if user_input.lower() == 'history':
                self.show_history()
                continue
                
            if user_input.lower() == 'clear':
                self.history.clear()
                self.print_message("History cleared.", MessageType.SUCCESS)
                continue
                
            # Check for detail/explain commands
            show_detail = False
            find_substrings = False
            
            if user_input.startswith('detail '):
                show_detail = True
                find_substrings = True
                user_input = user_input[7:].strip()
            elif user_input.startswith('explain '):
                show_detail = True
                user_input = user_input[8:].strip()
                
            if user_input:
                result = is_palindrome(user_input)
                norm_text = explain(user_input).normalized
                self.history.append((user_input, result, norm_text))
                self.check_text_cli(user_input, show_explain=show_detail, find_substrings=find_substrings)

def main(argv=None):
    """Main CLI entry point with enhanced argument parsing"""
    if not RICH_AVAILABLE:
        print("For the best experience, install rich: pip install rich")
    
    cli = EnhancedPalindromeCLI()
    parser = argparse.ArgumentParser(
        description="Palindrome Checker CLI with Enhanced Visuals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "A man, a plan, a canal: Panama"
  %(prog)s -e "Never odd or even"
  %(prog)s -s "Palindrome"
  %(prog)s -i  # Interactive mode

Install 'rich' for enhanced visuals: pip install rich
        """
    )
    
    parser.add_argument("text", nargs="*", help="Text to check")
    parser.add_argument("-e", "--explain", action="store_true", 
                       help="Show detailed explanation")
    parser.add_argument("-s", "--substrings", action="store_true",
                       help="Find palindromic substrings for non-palindromes")
    parser.add_argument("-i", "--interactive", action="store_true", 
                       help="Interactive mode")
    
    ns = parser.parse_args(argv)
    
    if ns.interactive:
        cli.interactive_cli()
        return
    
    if ns.text:
        text = " ".join(ns.text)
        cli.check_text_cli(text, show_explain=ns.explain, find_substrings=ns.substrings)
        return
    
    # Read from stdin if no arguments provided
    if not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            if line:
                cli.check_text_cli(line, show_explain=ns.explain, find_substrings=ns.substrings)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()