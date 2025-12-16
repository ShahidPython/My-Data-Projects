# cli.py — Enhanced Typer-powered CLI with Rich

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from typing import Optional
from storage import init_db, add_card, get_all_cards, delete_card, update_card, get_card

app = typer.Typer(help="Professional Flashcard App CLI")
console = Console()

@app.command()
def init():
    """Initialize the database."""
    init_db()
    console.print("[bold green]✓ Database initialized successfully![/bold green]")

@app.command()
def add(
    question: str = typer.Argument(..., help="Question text"),
    answer: str = typer.Argument(..., help="Answer text"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Category for the card")
):
    """Add a new flashcard."""
    add_card(question, answer, category)
    console.print(Panel.fit(
        f"[green]Card added successfully![/green]\n\n"
        f"[bold]Question:[/bold] {question}\n"
        f"[bold]Answer:[/bold] {answer}\n"
        f"[bold]Category:[/bold] {category if category else 'Uncategorized'}",
        title="✅ Success",
        border_style="green"
    ))

@app.command("list")
def list_cards(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category")
):
    """List all flashcards with optional category filter."""
    rows = get_all_cards(category)
    
    if not rows:
        console.print("[yellow]No cards found.[/yellow]")
        return
        
    table = Table(title="Flashcards", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Question", style="white", width=40)
    table.add_column("Answer", style="green", width=40)
    table.add_column("Category", style="yellow", width=15)
    
    for _id, q, a, c in rows:
        table.add_row(str(_id), q, a, c if c else "Uncategorized")
    
    console.print(table)

@app.command()
def study(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Study specific category"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Number of cards to study")
):
    """Study flashcards in interactive mode."""
    from random import shuffle
    
    cards = get_all_cards(category)
    if not cards:
        console.print("[yellow]No cards found to study.[/yellow]")
        return
        
    if limit and limit < len(cards):
        shuffle(cards)
        cards = cards[:limit]
    
    console.print(Panel.fit(
        f"Studying [bold]{len(cards)}[/bold] card{'s' if len(cards) > 1 else ''}\n"
        f"Press Enter to reveal answer, then rate your knowledge",
        title="📚 Study Mode",
        border_style="blue"
    ))
    
    correct = 0
    for i, (_id, question, answer, category) in enumerate(cards, 1):
        console.rule(f"Card {i} of {len(cards)}")
        console.print(f"\n[bold]Question:[/bold] {question}")
        input("\nPress Enter to reveal answer...")
        console.print(f"[bold green]Answer:[/bold] {answer}")
        
        knew_it = Confirm.ask("\nDid you know this?", default=False)
        if knew_it:
            correct += 1
            console.print("[green]✓ Good job![/green]")
        else:
            console.print("[yellow]✓ Keep practicing![/yellow]")
    
    console.rule("Study Session Complete")
    console.print(f"\n[bold]Score:[/bold] {correct}/{len(cards)} ({correct/len(cards)*100:.1f}%)")

@app.command()
def remove(
    card_id: int = typer.Argument(..., help="ID of the card to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation")
):
    """Delete a flashcard by ID."""
    card = get_card(card_id)
    if not card:
        console.print(f"[red]Card {card_id} not found[/red]")
        raise typer.Exit(1)
    
    _id, question, answer, category = card
    
    if not force:
        console.print(Panel.fit(
            f"[bold]Question:[/bold] {question}\n"
            f"[bold]Answer:[/bold] {answer}\n"
            f"[bold]Category:[/bold] {category if category else 'Uncategorized'}",
            title="⚠️ Confirm Deletion",
            border_style="red"
        ))
        confirm = Confirm.ask("Are you sure you want to delete this card?")
        if not confirm:
            console.print("[yellow]Deletion cancelled[/yellow]")
            return
    
    deleted = delete_card(card_id)
    if deleted:
        console.print(f"[green]✓ Card {card_id} deleted successfully[/green]")
    else:
        console.print(f"[red]Failed to delete card {card_id}[/red]")

@app.command()
def update(
    card_id: int = typer.Argument(..., help="ID of the card to update"),
    question: Optional[str] = typer.Option(None, "--question", "-q", help="New question text"),
    answer: Optional[str] = typer.Option(None, "--answer", "-a", help="New answer text"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="New category")
):
    """Update an existing flashcard."""
    card = get_card(card_id)
    if not card:
        console.print(f"[red]Card {card_id} not found[/red]")
        raise typer.Exit(1)
    
    _id, old_question, old_answer, old_category = card
    
    # Use existing values if not provided
    new_question = question if question is not None else old_question
    new_answer = answer if answer is not None else old_answer
    new_category = category if category is not None else old_category
    
    update_card(card_id, new_question, new_answer, new_category)
    
    console.print(Panel.fit(
        f"[green]Card updated successfully![/green]\n\n"
        f"[bold]Question:[/bold] {new_question}\n"
        f"[bold]Answer:[/bold] {new_answer}\n"
        f"[bold]Category:[/bold] {new_category if new_category else 'Uncategorized'}",
        title="✅ Updated",
        border_style="green"
    ))

@app.command()
def stats():
    """Show statistics about your flashcards."""
    from collections import defaultdict
    from storage import get_all_cards, get_categories
    
    cards = get_all_cards()
    categories = get_categories()
    
    if not cards:
        console.print("[yellow]No cards found.[/yellow]")
        return
    
    category_count = defaultdict(int)
    for _, _, _, category in cards:
        category_name = category if category else "Uncategorized"
        category_count[category_name] += 1
    
    table = Table(title="Flashcard Statistics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Cards", str(len(cards)))
    table.add_row("Total Categories", str(len(categories)))
    
    console.print(table)
    
    if categories:
        console.print("\n[bold]Cards by Category:[/bold]")
        for category, count in category_count.items():
            console.print(f"  {category}: {count}")

def run_interactive_cli():
    """Enhanced interactive CLI with rich interface."""
    init_db()
    
    while True:
        console.print(Panel.fit(
            "[bold cyan]Flashcard App[/bold cyan]\n"
            "Manage and study your flashcards efficiently",
            title="🎴 Main Menu",
            border_style="blue"
        ))
        
        console.print("1) 📝 Add new card")
        console.print("2) 📋 List all cards")
        console.print("3) 🔍 Search cards")
        console.print("4) 📚 Study mode")
        console.print("5) 📊 Statistics")
        console.print("6) 🗑️ Delete card")
        console.print("7) ✏️ Edit card")
        console.print("0) 🚪 Exit")
        
        choice = Prompt.ask("Choose an option", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "1":
            console.print(Panel.fit("Add New Flashcard", title="📝", border_style="green"))
            question = Prompt.ask("Question")
            answer = Prompt.ask("Answer")
            category = Prompt.ask("Category (optional)", default="")
            add_card(question, answer, category if category else None)
            console.print("[green]✓ Card added successfully![/green]")
            
        elif choice == "2":
            category = Prompt.ask("Filter by category (press Enter for all)", default="")
            list_cards(category if category else None)
            
        elif choice == "3":
            from storage import search_cards
            term = Prompt.ask("Search term")
            results = search_cards(term)
            if results:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("ID", style="cyan", width=4)
                table.add_column("Question", style="white", width=40)
                table.add_column("Answer", style="green", width=40)
                table.add_column("Category", style="yellow", width=15)
                
                for _id, q, a, c in results:
                    table.add_row(str(_id), q, a, c if c else "Uncategorized")
                
                console.print(table)
            else:
                console.print("[yellow]No matching cards found.[/yellow]")
                
        elif choice == "4":
            category = Prompt.ask("Study category (press Enter for all)", default="")
            limit = Prompt.ask("Number of cards (press Enter for all)", default="")
            study(
                category=category if category else None,
                limit=int(limit) if limit.isdigit() else None
            )
            
        elif choice == "5":
            stats()
            
        elif choice == "6":
            card_id = IntPrompt.ask("Card ID to delete")
            remove(card_id)
            
        elif choice == "7":
            card_id = IntPrompt.ask("Card ID to edit")
            card = get_card(card_id)
            if not card:
                console.print(f"[red]Card {card_id} not found[/red]")
                continue
                
            _id, question, answer, category = card
            console.print(f"Current question: {question}")
            new_question = Prompt.ask("New question (press Enter to keep current)", default=question)
            
            console.print(f"Current answer: {answer}")
            new_answer = Prompt.ask("New answer (press Enter to keep current)", default=answer)
            
            console.print(f"Current category: {category if category else 'Uncategorized'}")
            new_category = Prompt.ask("New category (press Enter to keep current)", default=category if category else "")
            
            update_card(
                card_id, 
                new_question if new_question != question else question,
                new_answer if new_answer != answer else answer,
                new_category if new_category != (category if category else "") else category
            )
            console.print("[green]✓ Card updated successfully![/green]")
            
        elif choice == "0":
            console.print("[blue]Goodbye! 👋[/blue]")
            break

if __name__ == "__main__":
    app()