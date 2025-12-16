from tipcalc.cli import run_menu, app
from tipcalc.gui import run as run_gui
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit(
        "💰 [bold cyan]Elegant Tip Calculator[/bold cyan] 💰", 
        style="bold blue", 
        subtitle="Choose your interface"
    ))
    
    console.print("\n[bold]Please select an option:[/bold]")
    console.print("1) 🖥️  CLI (Command Line Interface)")
    console.print("2) 🎨 GUI (Graphical User Interface)")
    console.print("3) ❓ Help")
    console.print("0) ❌ Exit")
    
    choice = input("> ").strip()
    
    if choice == "1":
        run_menu()
    elif choice == "2":
        run_gui()
    elif choice == "3":
        console.print("\n[bold]Help:[/bold]")
        console.print("CLI: Command line interface with rich text formatting")
        console.print("GUI: Graphical interface with sliders and real-time updates")
        console.print("\nYou can also run 'tipcalc --help' for CLI options")
        input("\nPress Enter to continue...")
        main()
    else:
        console.print("\n👋 [bold green]Thank you for using Elegant Tip Calculator![/bold green]")

if __name__ == "__main__":
    main()