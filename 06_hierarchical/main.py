"""
Startup Idea Validator — Entry Point
Runs the hierarchical multi-agent graph to validate a startup idea.
"""

from agents import build_main_graph
from state import OverallState

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.status import Status

console = Console()

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
            "[dim]Powered by hierarchical multi-agent analysis[/dim]",
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
    console.print("  :bar_chart:  [cyan]Market Research Team[/cyan]")
    console.print("  :gear:  [cyan]Technical Feasibility Team[/cyan]")
    console.print("  :money_bag:  [cyan]Financial Analysis Team[/cyan]")
    console.print()

    final = None
    with Status("[bold magenta]Agents are working...[/bold magenta]", console=console, spinner="dots"):
        for step in app.stream(initial_state, {"recursion_limit": 30}):
            node_name = list(step.keys())[0]
            final = step[node_name]
            label, emoji = NODE_LABELS.get(node_name, (node_name, "white_check_mark"))
            console.log(f":{emoji}:  [bold green]✓[/bold green] [white]{label}[/white] completed")

    if final is None:
        console.print("[bold red]Error: Pipeline produced no output.[/bold red]")
        return

    console.print()
    console.print(Rule("[bold blue]Individual Team Reports[/bold blue]"))

    # Market Research Report
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

    # Technical Feasibility Report
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

    # Financial Report
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

    # Final Combined Report
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
    console.print()


if __name__ == "__main__":
    main()
