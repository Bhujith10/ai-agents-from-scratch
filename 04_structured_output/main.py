from agent import triage_batch
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from mock_emails import mock_emails
from collections import Counter

CATEGORY_STYLES = {
    "urgent": "red",
    "needs_reply": "yellow",
    "fyi": "cyan",
    "spam": "dim",
}

def print_summary(console: Console, results):
    stats = Counter(r.category for r in results.results)

    table = Table(title="Triage Summary", show_lines=True)
    table.add_column("Category", style="bold")
    table.add_column("Count", justify="center")

    for category, style in CATEGORY_STYLES.items():
        table.add_row(f"[{style}]{category}[/{style}]", str(stats.get(category, 0)))

    table.add_row("[bold]Total[/bold]", str(len(results.results)))
    console.print(table)

def print_results(console: Console, results):
    for i, result in enumerate(results.results, 1):
        style = CATEGORY_STYLES.get(result.category, "white")

        content = (
            f"[bold]Category:[/bold] {result.category}\n"
            f"[bold]Confidence:[/bold] {result.confidence}\n"
            f"[bold]Reasoning:[/bold] {result.reasoning}"
        )

        if result.draft_reply:
            content += f"\n\n[bold]Draft Reply:[/bold]\n{result.draft_reply}"

        if result.confidence < 0.7:
            content += "\n\n[bold red]⚠ LOW CONFIDENCE — needs human review[/bold red]"

        console.print(Panel(content, title=f"Email {i}", border_style=style))

def main():
    console = Console()
    console.print("\n[bold]Running email triage...[/bold]\n")

    results = triage_batch(mock_emails)

    console.print()
    print_summary(console, results)
    console.print()
    print_results(console, results)

if __name__ == "__main__":
    main()


