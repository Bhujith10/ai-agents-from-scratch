import os
from dotenv import load_dotenv, find_dotenv
from prompts import SYSTEM_PROMPT
import openai
import json
from rich.console import Console
from tools import TOOLS

load_dotenv(find_dotenv())
console = Console()


class Agent:
    def __init__(self, model, max_iterations=5):
        self.model = model
        self.max_iterations = max_iterations
        self.history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _parse_json(self, content):
        """
        Parse JSON content from LLM response
        """
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        # extract first complete JSON object in case LLM outputs duplicates
        decoder = json.JSONDecoder()
        content = content.strip()
        try:
            parsed, _ = decoder.raw_decode(content)
            return parsed
        except json.JSONDecodeError:
            return {"Final Answer": f"Failed to parse response: {content}"}

    def _call_llm(self):
        """
        Call LLM and parse response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )
        self.history.append({"role": "assistant", "content": response.choices[0].message.content})
        return self._parse_json(response.choices[0].message.content.strip())

    def _print_response(self, response):
        """
        Print response in a formatted way
        """
        if "Thought" in response:
            console.print(f"[bold cyan]Thought:[/bold cyan] {response['Thought']}")
        if "Action" in response:
            console.print(f"[bold cyan]Action:[/bold cyan] {response['Action']}")
        if "Action Input" in response:
            console.print(f"[bold cyan]Action Input:[/bold cyan] {response['Action Input']}")
        if "Final Answer" in response:
            return

    def run(self, user_input):
        """
        Run the agent with user input
        """
        iteration = 0
        self.history.append({"role": "user", "content": user_input})
        while(iteration < self.max_iterations):
            response = self._call_llm()
            self._print_response(response)
            if "Action" in response:
                action = response["Action"]
                if action not in TOOLS:
                    self.history.append({"role": "user", "content": f"Observation: Tool '{action}' not found."})
                    continue
                action_input = response["Action Input"]
                result = TOOLS[action]["function"](action_input)
                result_text = f"Observation: {result}"
                self.history.append({"role": "user", "content": result_text})
                iteration += 1
            else:
                return response["Final Answer"]
        
        console.print("[bold red]Max iterations reached[/bold red]")
        return self.history[-1]["content"]

