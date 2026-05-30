"""
LangSmith Dashboard — Fetch and display trace data

Queries recent runs from LangSmith and displays:
- Token usage per run
- Cost breakdown
- Latency per node
- Run summary statistics

Run: python dashboard.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "06_hierarchical"))

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from langsmith import Client

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

console = Console()
client = Client()


def fetch_recent_runs(project_name: str, limit: int = 10):
    """Fetch recent top-level runs from LangSmith."""
    runs = list(client.list_runs(
        project_name=project_name,
        is_root=True,
        limit=limit,
    ))
    return runs


def fetch_child_runs(run_id: str):
    """Fetch child runs (node-level traces) for a given parent run."""
    runs = list(client.list_runs(
        trace_id=run_id,
        limit=100,
    ))
    return runs


def display_runs_summary(runs, project_name: str):
    """Display a summary table of recent runs."""
    table = Table(title=f"Recent Runs — {project_name}")
    table.add_column("#", style="dim", justify="right")
    table.add_column("Run ID", style="cyan", max_width=12)
    table.add_column("Status", justify="center")
    table.add_column("Duration", style="green", justify="right")
    table.add_column("Input Tokens", style="yellow", justify="right")
    table.add_column("Output Tokens", style="yellow", justify="right")
    table.add_column("Total Tokens", style="bold yellow", justify="right")
    table.add_column("Cost", style="bold green", justify="right")
    table.add_column("Time", style="dim", justify="right")

    for i, run in enumerate(runs, 1):
        run_id = str(run.id)[:12]
        status = "[green]✓[/green]" if run.status == "success" else f"[red]{run.status}[/red]"

        # Duration
        if run.end_time and run.start_time:
            duration = (run.end_time - run.start_time).total_seconds()
            duration_str = f"{duration:.1f}s"
        else:
            duration_str = "-"

        # Token usage
        token_usage = run.total_tokens or 0
        prompt_tokens = run.prompt_tokens or 0
        completion_tokens = run.completion_tokens or 0

        # Cost
        total_cost = run.total_cost
        cost_str = f"${total_cost:.4f}" if total_cost else "-"

        # Time
        time_str = run.start_time.strftime("%H:%M:%S") if run.start_time else "-"

        table.add_row(
            str(i),
            run_id,
            status,
            duration_str,
            str(prompt_tokens) if prompt_tokens else "-",
            str(completion_tokens) if completion_tokens else "-",
            str(token_usage) if token_usage else "-",
            cost_str,
            time_str,
        )

    console.print(table)


def display_run_details(run):
    """Display detailed breakdown of a single run."""
    run_id = str(run.id)

    console.print()
    console.print(Rule(f"[bold]Run Details: {run_id[:12]}...[/bold]"))
    console.print()

    # Basic info
    info_lines = [
        f"[bold]Run ID:[/bold] {run_id}",
        f"[bold]Status:[/bold] {run.status}",
    ]

    if run.start_time and run.end_time:
        duration = (run.end_time - run.start_time).total_seconds()
        info_lines.append(f"[bold]Duration:[/bold] {duration:.1f}s")

    if run.total_tokens:
        info_lines.append(f"[bold]Total Tokens:[/bold] {run.total_tokens:,}")
    if run.prompt_tokens:
        info_lines.append(f"[bold]Input Tokens:[/bold] {run.prompt_tokens:,}")
    if run.completion_tokens:
        info_lines.append(f"[bold]Output Tokens:[/bold] {run.completion_tokens:,}")
    if run.total_cost:
        info_lines.append(f"[bold]Total Cost:[/bold] ${run.total_cost:.4f}")

    # Tags and metadata
    if run.tags:
        info_lines.append(f"[bold]Tags:[/bold] {', '.join(run.tags)}")

    console.print(Panel(
        "\n".join(info_lines),
        title="[bold cyan]Run Summary[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    ))

    # Fetch child runs for node-level breakdown
    console.print()
    console.print("[dim]Fetching child traces...[/dim]")

    children = fetch_child_runs(run_id)

    if children:
        child_table = Table(title="Node-Level Breakdown")
        child_table.add_column("Node", style="cyan", justify="left")
        child_table.add_column("Type", style="dim", justify="center")
        child_table.add_column("Duration", style="green", justify="right")
        child_table.add_column("Tokens", style="yellow", justify="right")
        child_table.add_column("Cost", style="green", justify="right")
        child_table.add_column("Status", justify="center")

        # Sort by start time
        children.sort(key=lambda r: r.start_time or datetime.min.replace(tzinfo=timezone.utc))

        total_child_tokens = 0
        total_child_cost = 0.0

        for child in children:
            name = child.name or "-"
            run_type = child.run_type or "-"

            if child.start_time and child.end_time:
                child_duration = (child.end_time - child.start_time).total_seconds()
                child_duration_str = f"{child_duration:.1f}s"
            else:
                child_duration_str = "-"

            child_tokens = child.total_tokens or 0
            total_child_tokens += child_tokens

            child_cost = child.total_cost or 0.0
            total_child_cost += child_cost

            cost_str = f"${child_cost:.4f}" if child_cost else "-"
            status = "[green]✓[/green]" if child.status == "success" else f"[red]{child.status}[/red]"

            child_table.add_row(
                name,
                run_type,
                child_duration_str,
                str(child_tokens) if child_tokens else "-",
                cost_str,
                status,
            )

        child_table.add_row(
            "[bold]Total[/bold]",
            "",
            "",
            f"[bold]{total_child_tokens:,}[/bold]",
            f"[bold]${total_child_cost:.4f}[/bold]",
            "",
        )

        console.print(child_table)
    else:
        console.print("[dim]No child traces found.[/dim]")


def main():
    console.print()
    console.print(
        Panel(
            "[bold magenta]LangSmith Dashboard[/bold magenta]\n"
            "[dim]View traces, costs, and token usage[/dim]",
            border_style="magenta",
            padding=(1, 2),
        )
    )
    console.print()

    project_name = os.environ.get("LANGCHAIN_PROJECT", "startup-validator")
    console.print(f"[bold]Project:[/bold] {project_name}")
    console.print()

    # Fetch recent runs
    console.print("[dim]Fetching recent runs...[/dim]")
    runs = fetch_recent_runs(project_name)

    if not runs:
        console.print("[bold yellow]No runs found. Run main.py first to generate traces.[/bold yellow]")
        return

    display_runs_summary(runs, project_name)

    # Ask user if they want details
    console.print()
    choice = Prompt.ask(
        "[bold cyan]Enter run number for details (or 'q' to quit)[/bold cyan]",
        default="1",
    ).strip()

    if choice.lower() == "q":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(runs):
            display_run_details(runs[idx])
        else:
            console.print("[red]Invalid run number.[/red]")
    except ValueError:
        console.print("[red]Invalid input.[/red]")

    console.print()
    console.print(
        f"[dim]For full trace visualization, visit: https://smith.langchain.com[/dim]"
    )
    console.print()


if __name__ == "__main__":
    main()
