"""
Observability-Instrumented Startup Validator
Wraps Project 6 with LangSmith tracing, per-node latency, and metadata.

Run: python main.py
"""

import sys
import os
import time

# Add project 6 to path so we can import its modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "06_hierarchical"))

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Ensure LangSmith tracing is enabled
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "startup-validator")

import langsmith as ls
from langsmith import Client

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.status import Status
from rich.table import Table

from agents import build_main_graph
from state import OverallState

console = Console()
ls_client = Client()

NODE_LABELS = {
    "market_research": ("Market Research Team", "bar_chart"),
    "technical_feasibility": ("Technical Feasibility Team", "gear"),
    "financial_analysis": ("Financial Analysis Team", "money_bag"),
    "report_generator": ("Final Report Generator", "memo"),
}


def main():
    app = build_main_graph()

    console.print()
    console.print(
        Panel(
            "[bold cyan]Startup Idea Validator[/bold cyan]\n"
            "[dim]With LangSmith Observability[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    startup_idea = Prompt.ask(
        "[bold yellow]Enter your startup idea[/bold yellow]",
        default="An AI-powered personal finance assistant that automatically categorizes expenses, negotiates bills, and finds savings opportunities",
    ).strip()

    initial_state: OverallState = {
        "startup_idea": startup_idea,
        "market_research_report": "",
        "technical_feasibility_report": "",
        "financial_report": "",
        "final_report": "",
    }

    console.print()
    console.print(
        Panel(
            f"[bold white]{startup_idea}[/bold white]",
            title="[bold green]Startup Idea[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )
    console.print()
    console.print(Rule("[bold blue]Running Analysis Teams[/bold blue]"))
    console.print()

    # --- Run with LangSmith metadata and per-node latency tracking ---
    node_timings = {}
    final = None
    pipeline_start = time.time()

    with ls.tracing_context(
        metadata={
            "startup_idea": startup_idea[:200],
            "project": "07_observability",
        },
        tags=["startup-validator", "hierarchical", "observability"],
    ):
        with Status("[bold magenta]Agents are working...[/bold magenta]", console=console, spinner="dots"):
            for step in app.stream(initial_state, {"recursion_limit": 30}):
                node_name = list(step.keys())[0]
                node_start = node_timings.get(node_name, {}).get("start", time.time())
                node_end = time.time()

                if node_name not in node_timings:
                    node_timings[node_name] = {"start": pipeline_start if not node_timings else time.time()}

                node_timings[node_name]["end"] = node_end
                node_timings[node_name]["duration"] = node_end - node_timings[node_name]["start"]

                final = step[node_name]
                label, emoji = NODE_LABELS.get(node_name, (node_name, "white_check_mark"))
                duration = node_timings[node_name]["duration"]
                console.log(
                    f":{emoji}:  [bold green]✓[/bold green] [white]{label}[/white] "
                    f"completed [dim]({duration:.1f}s)[/dim]"
                )

    pipeline_end = time.time()
    total_duration = pipeline_end - pipeline_start

    if final is None:
        console.print("[bold red]Error: Pipeline produced no output.[/bold red]")
        return

    # --- Latency Summary Table ---
    console.print()
    console.print(Rule("[bold blue]Latency Summary[/bold blue]"))
    console.print()

    latency_table = Table(title="Per-Node Latency")
    latency_table.add_column("Node", style="cyan", justify="left")
    latency_table.add_column("Duration", style="green", justify="right")
    latency_table.add_column("% of Total", style="yellow", justify="right")

    for node_name, timing in node_timings.items():
        label, _ = NODE_LABELS.get(node_name, (node_name, ""))
        duration = timing["duration"]
        pct = (duration / total_duration) * 100 if total_duration > 0 else 0
        latency_table.add_row(label, f"{duration:.1f}s", f"{pct:.0f}%")

    latency_table.add_row("[bold]Total[/bold]", f"[bold]{total_duration:.1f}s[/bold]", "[bold]100%[/bold]")
    console.print(latency_table)

    # --- Individual Team Reports ---
    console.print()
    console.print(Rule("[bold blue]Individual Team Reports[/bold blue]"))

    market_report = final.get("market_research_report", "")
    if market_report:
        console.print()
        console.print(
            Panel(
                Markdown(market_report),
                title="[bold cyan]:bar_chart: Market Research Report[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        )

    tech_report = final.get("technical_feasibility_report", "")
    if tech_report:
        console.print()
        console.print(
            Panel(
                Markdown(tech_report),
                title="[bold yellow]:gear: Technical Feasibility Report[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    fin_report = final.get("financial_report", "")
    if fin_report:
        console.print()
        console.print(
            Panel(
                Markdown(fin_report),
                title="[bold green]:money_bag: Financial Analysis Report[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

    # --- Final Combined Report ---
    console.print()
    console.print(Rule("[bold red]Final Startup Validation Report[/bold red]"))
    console.print()

    final_report = final.get("final_report", "No report generated.")
    console.print(
        Panel(
            Markdown(final_report),
            title="[bold red]:rocket: Startup Validation Report[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
    )

    # --- LangSmith Info ---
    console.print()
    project_name = os.environ.get("LANGCHAIN_PROJECT", "startup-validator")
    console.print(
        Panel(
            f"[bold]Project:[/bold] {project_name}\n"
            f"[bold]Dashboard:[/bold] https://smith.langchain.com\n"
            f"[bold]Total Duration:[/bold] {total_duration:.1f}s\n\n"
            "[dim]View full traces, token usage, and costs in the LangSmith dashboard.[/dim]\n"
            "[dim]Run [bold]python dashboard.py[/bold] to fetch cost & token summary.[/dim]\n"
            "[dim]Run [bold]python evaluate.py[/bold] to score report quality with LLM-as-judge.[/dim]",
            title="[bold magenta]:eyes: LangSmith Observability[/bold magenta]",
            border_style="magenta",
            padding=(1, 2),
        )
    )
    console.print()

    return final


if __name__ == "__main__":
    main()

