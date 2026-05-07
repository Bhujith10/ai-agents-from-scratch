from agent import MemoryAgent
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():

    user_id = str(input("Enter user ID: "))
    agent = MemoryAgent(user_id=user_id)
    console.print(Panel.fit(f"Memory Agent Initialized for {user_id}", title="Agent Status"))

    while True:
        try:
            user_input = input("You: ")
            if not user_input.strip():
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print(Panel.fit("Goodbye!", title="Agent Status"))
                break
            response = agent.chat(user_input)
            console.print(Panel.fit(response, title="Agent Response"))
        except KeyboardInterrupt:
            console.print(Panel.fit("Goodbye!", title="Agent Status"))
            break
        except Exception as e:
            console.print(Panel.fit(f"Error: {e}", title="Error"))
    

if __name__ == "__main__":
    main()
