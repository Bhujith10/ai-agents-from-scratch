from memory import MemoryStore
import openai
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class MemoryAgent:
    def __init__(self, user_id: str, model: str = "gpt-5.4-mini"):
        self.memory = MemoryStore(user_id)
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.system_prompt = self._build_system_prompt()
        self.history = [
            {"role": "system", "content": self.system_prompt}
        ]


    def _build_system_prompt(self, condensed_memory: str = None) -> str:
        memory_context = condensed_memory if condensed_memory else self._summarize_memory()
        memory_section = f"\n        {memory_context}" if memory_context else "\n        No previous interactions on record."
        return (
            "You are a knowledgeable and empathetic personal finance advisor. "
            "You provide clear, actionable, and personalized financial guidance. "
            "Always refer to what you know about the user to give tailored advice. "
            "Be concise but thorough. If you lack information to give specific advice, ask a clarifying question."
            f"\n\n        What you know about this user from past interactions:{memory_section}"
        )
    
    def chat(self, message: str):
        self.history.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )
        self.history.append({"role": "assistant", "content": response.choices[0].message.content})

        if len(self.history) > 10:
            print("Memory limit reached, summarizing...")
            condensed_memory = self._condense_and_update_memory(self.history)
            self.history = [
                {"role": "system", "content": self._build_system_prompt(condensed_memory)},
                {"role": "assistant", "content": "I've noted our conversation so far. Please continue."}
            ]

        return response.choices[0].message.content

    def _condense_and_update_memory(self, history) -> str:
        conversation = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])
        condense_prompt = (
            "You are summarizing a financial advisory conversation to retain key user information.\n\n"
            "Extract and summarize the following into a compact memory note:\n"
            "- Financial goals and targets (amounts, deadlines)\n"
            "- Income, expenses, savings figures mentioned\n"
            "- User preferences and constraints\n"
            "- Decisions made or advice accepted\n"
            "- Any recurring concerns\n\n"
            f"Conversation:\n{conversation}\n\n"
            "Write the memory note in third-person (e.g. 'The user wants to...'). Be specific and concise."
        )
        condense_response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": condense_prompt}]
        )
        self.memory.save(condense_response.choices[0].message.content)
        return condense_response.choices[0].message.content
        
    
    def _summarize_memory(self) -> str:
        docs = self.memory.retrieve_all()
        if not docs:
            return ""
        all_memories = "\n".join(f"- {doc}" for doc in docs)
        summary_prompt = (
            "You are preparing a user profile summary for a financial advisor.\n\n"
            "Based on the following stored memory notes, produce a single cohesive summary of:\n"
            "- The user's financial goals and targets\n"
            "- Known income, expenses, or savings figures\n"
            "- Preferences, constraints, and recurring concerns\n\n"
            f"Memory notes:\n{all_memories}\n\n"
            "Write in third-person. Avoid redundancy. Be specific."
        )
        summary_response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": summary_prompt}]
        )
        return summary_response.choices[0].message.content


if __name__ == "__main__":
    agent = MemoryAgent(user_id="user_1")
    print("Agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        response = agent.chat(user_input)
        print(f"Agent: {response}\n")