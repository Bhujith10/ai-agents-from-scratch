from agent import Agent
from rich.console import Console

console = Console()

if __name__ == "__main__":
    agent = Agent("gpt-5.4-mini", max_iterations=5)
    console.print("[bold blue]Agent initialized[/bold blue]")
    console.print(f"[bold]Model:[/bold] {agent.model}")
    try:
        while True:
            user_input = input("User: ")

            if user_input.lower() in ["exit", "quit", "q"]:
                break

            if not user_input.strip():
                continue
            
            result = agent.run(user_input)
            console.print(f"[bold green]Final Answer:[/bold green] {result}")
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exiting...[/bold yellow]")
        
    