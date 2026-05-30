"""
LLM-as-Judge Evaluation for Startup Validation Reports

Scores a final report on multiple dimensions using a structured rubric.
Can be run standalone or after main.py.

Run: python evaluate.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "06_hierarchical"))

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "startup-validator")

from typing import Literal
from pydantic import BaseModel, Field

import langsmith as ls
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

console = Console()
llm = ChatOpenAI(model="gpt-5.4-mini")


# ---------------------------------------------------------------------------
# Evaluation Schema
# ---------------------------------------------------------------------------

class DimensionScore(BaseModel):
    score: int = Field(..., ge=1, le=5, description="Score from 1 (poor) to 5 (excellent)")
    reasoning: str = Field(..., description="Brief justification for the score")


class ReportEvaluation(BaseModel):
    completeness: DimensionScore = Field(..., description="Are all required sections present and substantive?")
    accuracy: DimensionScore = Field(..., description="Are claims grounded in data, not fabricated?")
    actionability: DimensionScore = Field(..., description="Are recommendations specific and actionable?")
    clarity: DimensionScore = Field(..., description="Is the report clear, well-structured, and readable?")
    critical_thinking: DimensionScore = Field(..., description="Does the report show genuine analysis, not just optimistic summaries?")
    overall_verdict: str = Field(..., description="One-sentence summary of report quality")


JUDGE_SYSTEM = """You are a senior VC partner and startup evaluator. You are reviewing an AI-generated
startup validation report. Score it on the following 5 dimensions (1-5 each):

## Scoring Rubric

### 1. Completeness (1-5)
- 5: All sections present with specific data points (market size figures, competitor names, cost estimates)
- 3: Most sections present but some lack depth or specifics
- 1: Major sections missing or entirely generic

### 2. Accuracy (1-5)
- 5: All claims appear grounded, sources cited, assumptions stated
- 3: Mix of grounded claims and unsupported assertions
- 1: Contains fabricated statistics or clearly wrong claims

### 3. Actionability (1-5)
- 5: Recommendations are specific, prioritized, with clear owners and timelines
- 3: Recommendations exist but are vague ("do market research")
- 1: No actionable recommendations

### 4. Clarity (1-5)
- 5: Well-structured, concise, easy to scan, professional tone
- 3: Readable but verbose or poorly organized
- 1: Confusing, poorly formatted, or incoherent

### 5. Critical Thinking (1-5)
- 5: Shows genuine risk analysis, identifies weaknesses, includes non-obvious insights
- 3: Surface-level analysis, acknowledges risks generically
- 1: Purely optimistic, no real critique or risk assessment

Provide a score and brief reasoning for each dimension.
End with a one-sentence overall verdict."""


@ls.traceable(
    run_type="chain",
    name="LLM-as-Judge Evaluation",
    tags=["evaluation", "llm-as-judge"],
    metadata={"evaluation_type": "report_quality"},
)
def evaluate_report(startup_idea: str, report: str) -> ReportEvaluation:
    """Evaluate a startup validation report using LLM-as-judge."""
    messages = [
        SystemMessage(content=JUDGE_SYSTEM),
        HumanMessage(content=f"""Startup Idea: {startup_idea}

Report to evaluate:
{report}
"""),
    ]

    structured_llm = llm.with_structured_output(ReportEvaluation)
    evaluation = structured_llm.invoke(messages)
    return evaluation


def display_evaluation(evaluation: ReportEvaluation):
    """Display evaluation results in a rich table."""
    table = Table(title="Report Quality Evaluation")
    table.add_column("Dimension", style="cyan", justify="left")
    table.add_column("Score", style="bold", justify="center")
    table.add_column("Rating", justify="center")
    table.add_column("Reasoning", style="dim", justify="left", max_width=60)

    dimensions = [
        ("Completeness", evaluation.completeness),
        ("Accuracy", evaluation.accuracy),
        ("Actionability", evaluation.actionability),
        ("Clarity", evaluation.clarity),
        ("Critical Thinking", evaluation.critical_thinking),
    ]

    total_score = 0
    for name, dim in dimensions:
        score = dim.score
        total_score += score

        if score >= 4:
            rating = "[green]★★★★★"[:score * 2 - 1] + "[/green]"
            score_style = "green"
        elif score >= 3:
            rating = "[yellow]★★★[/yellow]"
            score_style = "yellow"
        else:
            rating = "[red]★★[/red]" if score == 2 else "[red]★[/red]"
            score_style = "red"

        stars = "★" * score + "☆" * (5 - score)
        if score >= 4:
            stars_colored = f"[green]{stars}[/green]"
        elif score >= 3:
            stars_colored = f"[yellow]{stars}[/yellow]"
        else:
            stars_colored = f"[red]{stars}[/red]"

        table.add_row(
            name,
            f"[{score_style}]{score}/5[/{score_style}]",
            stars_colored,
            dim.reasoning,
        )

    avg = total_score / 5
    avg_style = "green" if avg >= 4 else "yellow" if avg >= 3 else "red"
    table.add_row(
        "[bold]Average[/bold]",
        f"[bold {avg_style}]{avg:.1f}/5[/bold {avg_style}]",
        "",
        "",
    )

    console.print(table)
    console.print()
    console.print(
        Panel(
            f"[italic]{evaluation.overall_verdict}[/italic]",
            title="[bold]Overall Verdict[/bold]",
            border_style="magenta",
            padding=(1, 2),
        )
    )


def main():
    console.print()
    console.print(Rule("[bold magenta]LLM-as-Judge Report Evaluation[/bold magenta]"))
    console.print()

    startup_idea = Prompt.ask(
        "[bold yellow]Enter the startup idea that was evaluated[/bold yellow]",
        default="An AI-powered personal finance assistant that automatically categorizes expenses, negotiates bills, and finds savings opportunities",
    ).strip()

    console.print()
    console.print("[dim]Paste the final report below. Enter an empty line to finish:[/dim]")
    console.print()

    lines = []
    while True:
        try:
            line = input()
            if line == "":
                if lines:
                    break
            lines.append(line)
        except EOFError:
            break

    report = "\n".join(lines)

    if not report.strip():
        console.print("[bold red]No report provided. Exiting.[/bold red]")
        return

    console.print()
    console.print("[bold cyan]Evaluating report quality...[/bold cyan]")
    console.print()

    evaluation = evaluate_report(startup_idea, report)
    display_evaluation(evaluation)

    console.print()
    console.print(
        "[dim]This evaluation trace is visible in LangSmith under the 'startup-validator' project.[/dim]"
    )
    console.print()


if __name__ == "__main__":
    main()
