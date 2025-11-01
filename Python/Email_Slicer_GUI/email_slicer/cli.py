"""Typer CLI for Email Slicer."""
from __future__ import annotations
import json
import sys
from typing import Optional, List
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
import questionary

from email_slicer.core import parse_email, EmailSliceError, batch_parse_emails
from email_slicer.validators import suggest_domain, get_email_provider_type

app = typer.Typer(
    help="Email Slicer — Extract and analyze email address components",
    rich_markup_mode="rich"
)
console = Console()

def _print_parsed_email(pe, json_out: bool = False, show_all: bool = False):
    """Print parsed email in formatted table or JSON."""
    if json_out:
        console.print_json(data={k: v for k, v in pe.__dict__.items()})
        return

    # Create a rich table with better formatting
    table = Table(
        title=f"[bold cyan]Parsed Email:[/bold cyan] [green]{pe.original}[/green]",
        box=box.ROUNDED,
        header_style="bold blue",
        title_style="bold cyan",
        show_header=True
    )
    
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    # Basic components (always shown)
    basic_fields = ["local_part", "base_username", "domain", "normalized"]
    for field in basic_fields:
        value = getattr(pe, field)
        table.add_row(field.replace("_", " ").title(), str(value))
    
    # Optional components
    if pe.tag:
        table.add_row("Tag", f"[yellow]{pe.tag}[/yellow]")
    
    # Extended components (shown with --all flag)
    if show_all:
        extended_fields = ["subdomain", "root_domain", "tld"]
        for field in extended_fields:
            value = getattr(pe, field)
            if value:
                table.add_row(field.replace("_", " ").title(), value)
        
        if hasattr(pe, 'is_disposable') and pe.is_disposable:
            table.add_row("Disposable", "[red]Yes[/red]")
        else:
            table.add_row("Disposable", "[green]No[/green]")
        
        provider_type = get_email_provider_type(pe.domain)
        table.add_row("Provider Type", f"[blue]{provider_type.title()}[/blue]")
    
    console.print(table)

def interactive_mode():
    """Run CLI in interactive mode."""
    console.print("\n[bold cyan]Email Slicer CLI - Interactive Mode[/bold cyan]")
    console.print("Type 'exit' to quit or 'help' for options\n")
    
    while True:
        try:
            command = questionary.text("📧 Enter email or command:").ask()
            
            if not command or command.lower() in ['exit', 'quit']:
                console.print("👋 Goodbye!")
                break
                
            if command.lower() == 'help':
                console.print("\n[bold]Available commands:[/bold]")
                console.print("• [green]email@example.com[/green] - Parse a single email")
                console.print("• [green]batch filename.txt[/green] - Process a batch file")
                console.print("• [green]validate email@example.com[/green] - Validate an email")
                console.print("• [green]exit[/green] - Quit the application")
                console.print("• [green]help[/green] - Show this help\n")
                continue
                
            if command.startswith('batch '):
                filename = command[6:].strip()
                if filename:
                    process_batch_file(filename, show_all=True)
                else:
                    console.print("[red]Error: Please specify a filename[/red]")
                continue
                
            if command.startswith('validate '):
                email = command[9:].strip()
                if email:
                    validate_email_interactive(email)
                else:
                    console.print("[red]Error: Please specify an email[/red]")
                continue
                
            # Assume it's an email to parse
            try:
                pe = parse_email(command, check_disposable=True)
                _print_parsed_email(pe, show_all=True)
                
                # Provide suggestions if available
                suggestion = suggest_domain(pe.domain)
                if suggestion:
                    console.print(f"\n[yellow]⚠️  Suggestion:[/yellow] Did you mean [bold]{suggestion}[/bold]?")
                    
            except EmailSliceError as exc:
                console.print(f"[red]❌ Invalid email:[/red] {exc}")
                
        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

def process_batch_file(filename, show_all=False):
    """Process a batch file in interactive mode."""
    file_path = Path(filename)
    if not file_path.exists():
        console.print(f"[red]❌ File not found:[/red] {filename}")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip()]
    except Exception as e:
        console.print(f"[red]❌ Error reading file:[/red] {e}")
        return

    if not lines:
        console.print("[yellow]⚠️  File is empty[/yellow]")
        return

    # Parse all emails with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Processing emails...", total=len(lines))
        
        parsed_emails = []
        for email in lines:
            try:
                parsed = parse_email(email, check_disposable=show_all)
                parsed_emails.append(parsed)
            except EmailSliceError:
                pass
            progress.update(task, advance=1)

    invalid_count = len(lines) - len(parsed_emails)

    # Display summary
    console.print(Panel.fit(
        f"[green]✓ Valid emails:[/green] {len(parsed_emails)}\n"
        f"[red]✗ Invalid emails:[/red] {invalid_count}",
        title="Batch Processing Summary",
        border_style="blue"
    ))

    # Display each parsed email
    for i, pe in enumerate(parsed_emails, 1):
        console.print(f"\n[bold cyan]{i}. [/bold cyan]", end="")
        _print_parsed_email(pe, show_all=show_all)

def validate_email_interactive(email):
    """Validate email in interactive mode."""
    from email_slicer.validators import validate_email_format, get_email_provider_type
    
    is_valid_format = validate_email_format(email)
    
    # Detailed validation
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Check", style="cyan", width=20)
    table.add_column("Result", style="green", width=10)
    table.add_column("Details", style="white")
    
    table.add_row("Format Validation", 
                 "[green]PASS[/green]" if is_valid_format else "[red]FAIL[/red]",
                 "Basic email format check")
    
    if is_valid_format:
        try:
            pe = parse_email(email)
            provider_type = get_email_provider_type(pe.domain)
            table.add_row("Provider Type", f"[blue]{provider_type.title()}[/blue]", "Email service category")
            
            if hasattr(pe, 'is_disposable') and pe.is_disposable:
                table.add_row("Disposable", "[red]YES[/red]", "Temporary email address")
            else:
                table.add_row("Disposable", "[green]NO[/green]", "Not a temporary email service")
                
        except EmailSliceError:
            table.add_row("Detailed Parsing", "[red]FAIL[/red]", "Cannot parse valid format email")
    
    console.print(Panel.fit(table, title=f"Email Validation: {email}"))

@app.command()
def slice(
    email: str = typer.Argument(..., help="Email address to parse"),
    json: bool = typer.Option(False, "--json", "-j", help="Output in JSON format"),
    all: bool = typer.Option(False, "--all", "-a", help="Show all components including extended info")
):
    """Slice a single EMAIL and print components."""
    try:
        pe = parse_email(email, check_disposable=all)
    except EmailSliceError as exc:
        console.print(f"[red]❌ Invalid email:[/red] {exc}")
        raise typer.Exit(code=1)

    _print_parsed_email(pe, json_out=json, show_all=all)
    
    # Provide suggestions if available
    suggestion = suggest_domain(pe.domain)
    if suggestion:
        console.print(f"\n[yellow]⚠️  Suggestion:[/yellow] Did you mean [bold]{suggestion}[/bold]?")

@app.command()
def batch(
    path: str = typer.Argument(..., help="Path to file containing emails (one per line)"),
    json: bool = typer.Option(False, "--json", "-j", help="Output in JSON format"),
    all: bool = typer.Option(False, "--all", "-a", help="Show all components including extended info"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Process multiple emails from a file."""
    file_path = Path(path)
    if not file_path.exists():
        console.print(f"[red]❌ File not found:[/red] {path}")
        raise typer.Exit(code=2)

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip()]
    except Exception as e:
        console.print(f"[red]❌ Error reading file:[/red] {e}")
        raise typer.Exit(code=3)

    if not lines:
        console.print("[yellow]⚠️  File is empty[/yellow]")
        return

    # Parse all emails with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Processing emails...", total=len(lines))
        
        parsed_emails = []
        for email in lines:
            try:
                parsed = parse_email(email, check_disposable=all)
                parsed_emails.append(parsed)
            except EmailSliceError:
                pass
            progress.update(task, advance=1)

    invalid_count = len(lines) - len(parsed_emails)

    if json:
        results = [pe.__dict__ for pe in parsed_emails]
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            console.print(f"[green]✓ Results saved to:[/green] {output}")
        else:
            console.print_json(data=results)
        return

    # Display summary
    console.print(Panel.fit(
        f"[green]✓ Valid emails:[/green] {len(parsed_emails)}\n"
        f"[red]✗ Invalid emails:[/red] {invalid_count}",
        title="Batch Processing Summary",
        border_style="blue"
    ))

    # Display each parsed email
    for i, pe in enumerate(parsed_emails, 1):
        console.print(f"\n[bold cyan]{i}. [/bold cyan]", end="")
        _print_parsed_email(pe, show_all=all)

    # Save to file if output specified
    if output:
        results = [pe.__dict__ for pe in parsed_emails]
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[green]✓ Results saved to:[/green] {output}")

@app.command()
def validate(
    email: str = typer.Argument(..., help="Email address to validate"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed validation info")
):
    """Validate an email address format and provider."""
    from email_slicer.validators import validate_email_format, get_email_provider_type
    
    is_valid_format = validate_email_format(email)
    
    if not detailed:
        status = "[green]VALID[/green]" if is_valid_format else "[red]INVALID[/red]"
        console.print(f"Email: {email} → {status}")
        return
    
    # Detailed validation
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Check", style="cyan", width=20)
    table.add_column("Result", style="green", width=10)
    table.add_column("Details", style="white")
    
    table.add_row("Format Validation", 
                 "[green]PASS[/green]" if is_valid_format else "[red]FAIL[/red]",
                 "Basic email format check")
    
    if is_valid_format:
        try:
            pe = parse_email(email)
            provider_type = get_email_provider_type(pe.domain)
            table.add_row("Provider Type", f"[blue]{provider_type.title()}[/blue]", "Email service category")
            
            if hasattr(pe, 'is_disposable') and pe.is_disposable:
                table.add_row("Disposable", "[red]YES[/red]", "Temporary email address")
            else:
                table.add_row("Disposable", "[green]NO[/green]", "Not a temporary email service")
                
        except EmailSliceError:
            table.add_row("Detailed Parsing", "[red]FAIL[/red]", "Cannot parse valid format email")
    
    console.print(Panel.fit(table, title=f"Email Validation: {email}"))

def main():
    """Main entry point for the CLI."""
    # If no arguments provided, run in interactive mode
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        app()

if __name__ == "__main__":
    main()