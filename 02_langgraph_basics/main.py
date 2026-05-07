from agent import build_graph
from rich.console import Console
from rich.panel import Panel
from langchain_core.messages import HumanMessage


console = Console()

def main():

    messages = []

    app = build_graph().compile()

    console.print("[bold cyan]GitHub Repo Documentation Helper[/bold cyan]")
    console.print("Enter a GitHub repo URL to analyze, then ask follow-up questions.")
    console.print("Type 'exit', 'quit', or 'q' to quit.\n")

    while True:
        try:
            user_input = console.input("[bold green]You:[/bold green] ")
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                break

            messages.append(HumanMessage(content=user_input))
            result = app.invoke({
                "messages": messages
            })
            console.print(Panel(result["messages"][-1].content, title="Agent Response", border_style="blue"))
            messages = result["messages"]

        except KeyboardInterrupt:
            break

        except Exception as e:
            console.print(Panel(str(e), title="Error", border_style="red"))

    console.print("\n[cyan]Goodbye![/cyan]")

if __name__ == "__main__":
    main()