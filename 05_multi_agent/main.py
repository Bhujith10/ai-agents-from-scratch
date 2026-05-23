"""
Content Pipeline CLI — Rich output
Run: python main.py
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.rule import Rule

from graph import build_graph
from state import ContentState

console = Console()

NODE_STYLES = {
    "supervisor":  ("bold cyan",    "🧠"),
    "researcher":  ("bold green",   "🔍"),
    "writer":      ("bold yellow",  "✍️"),
    "editor":      ("bold magenta", "📝"),
    "seo_writer":  ("bold blue",    "📈"),
}


def main():
    console.print(Rule("[bold]Content Pipeline[/bold]"))
    topic = Prompt.ask("[bold cyan]Enter the topic for the blog post[/bold cyan]")

    app = build_graph()

    initial_state: ContentState = {
        "topic": topic,
        "research": "",
        "draft": "",
        "editor_feedback": "",
        "seo_output": "",
        "current_agent": "",
        "iteration_count": 0,
        "research_count": 0,
        "final_post": "",
    }

    console.print(Rule("[dim]Pipeline started[/dim]"))

    final = None
    for step in app.stream(initial_state, {"recursion_limit": 25}):
        node_name = list(step.keys())[0]
        final = step[node_name]

        style, icon = NODE_STYLES.get(node_name, ("white", "⚙️"))
        console.print(
            f"  {icon} [{style}]{node_name}[/{style}] "
            f"[dim]| next → {final.get('current_agent', '-')} "
            f"| iteration {final.get('iteration_count', 0)}[/dim]"
        )

    console.print(Rule("[dim]Pipeline complete[/dim]"))

    # --- Final Post ---
    post = final.get("final_post") or final.get("draft", "")
    console.print(Panel(
        Markdown(post),
        title="[bold green]Final Blog Post[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))

    # --- SEO Output ---
    seo = final.get("seo_output", "")
    if seo:
        console.print(Panel(
            Markdown(seo),
            title="[bold blue]SEO Package[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        ))

    return final


if __name__ == "__main__":
    main()
