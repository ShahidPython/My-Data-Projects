from __future__ import annotations
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt, IntPrompt, FloatPrompt
from rich.layout import Layout
from rich.text import Text
import time
from .core import compute_tip, format_money
from . import __version__

app = typer.Typer(add_completion=False, help="✨ Elegant Tip Calculator CLI ✨")
console = Console()

def _print_header():
    console.print(Panel.fit(
        "💰 [bold cyan]Elegant Tip Calculator[/bold cyan] 💰", 
        style="bold blue on white", 
        subtitle=f"Version {__version__}"
    ))

def _print_result(res):
    # Create a beautiful result display
    result_table = Table(
        title="[bold green]Tip Calculation Results[/bold green]", 
        box=box.ROUNDED,
        header_style="bold magenta",
        title_style="bold green",
        expand=True
    )
    
    result_table.add_column("Description", style="cyan", justify="left")
    result_table.add_column("Amount", style="bold green", justify="right")
    
    result_table.add_row("Bill Amount", format_money(res.bill))
    result_table.add_row(f"Tip Percentage", f"{res.tip_pct}%")
    result_table.add_row("Tip Amount", format_money(res.tip_amount))
    result_table.add_row("Total Amount", format_money(res.total))
    result_table.add_row(f"Per Person (x{res.people})", format_money(res.per_person))
    
    if res.rounded:
        result_table.add_section()
        rounding_info = f"[yellow]{res.round_mode}[/yellow] to [yellow]{res.round_step}[/yellow] on [yellow]{res.round_target}[/yellow]"
        result_table.add_row("Rounding Applied", rounding_info)
    
    console.print()
    console.print(Panel(result_table, border_style="green"))
    console.print()

@app.command()
def calc(
    bill: float = typer.Argument(..., help="Total bill amount"),
    tip_pct: float = typer.Option(15.0, "--tip", "-t", help="Tip percentage"),
    people: int = typer.Option(1, "--people", "-p", help="Number of people splitting"),
    round_to: float = typer.Option(None, "--round-to", help="Step to round to (e.g., 0.05, 1.00)"),
    round_target: str = typer.Option("none", "--round-target", help="none|total|per_person|tip"),
    round_mode: str = typer.Option("nearest", "--round-mode", help="nearest|up|down"),
):
    """
    Calculate tip from the command line with beautiful output.
    """
    _print_header()
    
    # Show progress animation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Calculating...", total=None)
        time.sleep(0.8)  # Simulate calculation time
        
    res = compute_tip(
        bill=bill,
        tip_pct=tip_pct,
        people=people,
        round_to=round_to,
        round_target=round_target,
        round_mode=round_mode,
    )
    _print_result(res)

@app.command()
def interactive():
    """Interactive mode with beautiful prompts."""
    _print_header()
    
    console.print("\n[bold]Please enter your details:[/bold]\n")
    
    bill = FloatPrompt.ask("💵 [cyan]Bill amount[/cyan]", default=0.0)
    tip_pct = FloatPrompt.ask("💯 [cyan]Tip percentage[/cyan]", default=15.0)
    people = IntPrompt.ask("👥 [cyan]Number of people[/cyan]", default=1)
    
    use_rounding = Confirm.ask("🔄 [cyan]Apply rounding?[/cyan]", default=False)
    
    round_to = None
    round_target = "none"
    round_mode = "nearest"
    
    if use_rounding:
        round_to = FloatPrompt.ask("🎯 [cyan]Round to step[/cyan]", default=0.05)
        round_target = Prompt.ask(
            "🎯 [cyan]Round target[/cyan]", 
            choices=["none", "total", "per_person", "tip"], 
            default="per_person"
        )
        round_mode = Prompt.ask(
            "🔄 [cyan]Round mode[/cyan]", 
            choices=["nearest", "up", "down"], 
            default="nearest"
        )

    # Show progress animation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Calculating...", total=None)
        time.sleep(0.8)  # Simulate calculation time
        
    res = compute_tip(
        bill=bill,
        tip_pct=tip_pct,
        people=people,
        round_to=round_to,
        round_target=round_target,
        round_mode=round_mode,
    )
    _print_result(res)

@app.callback()
def version_callback(
    version: bool = typer.Option(None, "--version", "-v", help="Show version", is_eager=True)
):
    if version:
        console.print(f"✨ [bold green]tipcalc[/bold green] version [cyan]{__version__}[/cyan] ✨")
        raise typer.Exit()

def run_menu():
    """Run the menu interface."""
    _print_header()
    
    while True:
        console.print("\n[bold]Please choose an option:[/bold]")
        console.print("1) 🚀 Run interactive CLI")
        console.print("2) 💫 Quick calculation")
        console.print("0) ❌ Exit")
        
        choice = Prompt.ask(">", choices=["0", "1", "2"], default="1")
        
        if choice == "1":
            interactive()
        elif choice == "2":
            console.print("\n[bold]Quick Calculation:[/bold]")
            bill = FloatPrompt.ask("💵 Bill amount", default=100.0)
            tip_pct = FloatPrompt.ask("💯 Tip percentage", default=15.0)
            people = IntPrompt.ask("👥 Number of people", default=1)
            
            res = compute_tip(bill=bill, tip_pct=tip_pct, people=people)
            _print_result(res)
        else:
            console.print("\n👋 [bold green]Thank you for using Elegant Tip Calculator![/bold green]")
            break