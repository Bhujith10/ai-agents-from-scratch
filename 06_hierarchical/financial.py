"""
Financial Analysis Subgraph

Flow:
  START -> analyst -> financial_validator
    (loop back to analyst if NEEDS_MORE_WORK, max 3 iterations)
    -> financial_report -> END
"""

from dotenv import load_dotenv, find_dotenv
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from state import FinancialState

load_dotenv(find_dotenv())

MAX_ITERATIONS = 3

llm = ChatOpenAI(model="gpt-5.4-mini")


class ValidatorDecision(BaseModel):
    status: Literal["APPROVED", "NEEDS_MORE_WORK"]
    feedback: str


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def analyst_node(state: FinancialState) -> FinancialState:
    """Analyzes financial viability of the startup idea."""
    idea = state["startup_idea"]
    feedback = state.get("validator_feedback", "")
    previous_output = state.get("analyst_output", "")
    iteration = state.get("iteration_count", 0)

    prior_context = ""
    if previous_output:
        prior_context = f"""\n\n## Previous Analysis (iteration {iteration})
{previous_output}

## Validator Feedback (address these concerns specifically)
{feedback}"""

    messages = [
        SystemMessage(content="""You are a startup financial analyst with VC and CFO experience.
Perform a rigorous financial viability assessment for the given startup idea.

## Required analysis (use these sections)
1. **Revenue Model** — Identify 2-3 viable monetization strategies. For each: pricing approach,
   target customer segment, and why it fits this product.
2. **Unit Economics** — Estimate Customer Acquisition Cost (CAC), Lifetime Value (LTV),
   LTV:CAC ratio, gross margins. Use ranges (e.g., "$50-$150 CAC") when exact figures
   are uncertain. State your assumptions explicitly.
3. **Startup Costs** — Pre-launch capital needed: engineering, legal, marketing, infrastructure.
   Break down by category.
4. **Monthly Burn Rate** — Projected monthly operating costs for the first 12-18 months.
   Team salaries, cloud/infra, marketing, tools, legal/compliance.
5. **Path to Profitability** — At what scale (users/revenue) does this break even?
   Estimate months-to-breakeven under optimistic and realistic scenarios.
6. **Funding Strategy** — Recommended funding stages (bootstrapped → pre-seed → seed → Series A).
   How much to raise at each stage and what milestones justify each round.
7. **Financial Risks** — List each risk with severity (Critical/High/Medium/Low):
   pricing pressure, customer churn, regulatory costs, market timing, dependency on
   paid acquisition, etc.

## Rules
- Use realistic ranges, not single-point estimates. State assumptions.
- Compare to industry benchmarks where possible (e.g., "typical SaaS gross margin is 70-80%").
- If this is a follow-up iteration, DO NOT rewrite from scratch. Refine your previous analysis
  by addressing the validator's specific concerns."""),
        HumanMessage(content=f"Startup Idea: {idea}{prior_context}"),
    ]

    response = llm.invoke(messages)
    return {
        **state,
        "analyst_output": response.content.strip(),
        "iteration_count": iteration + 1,
    }


def financial_validator_node(state: FinancialState) -> FinancialState:
    """Critically validates the analyst's financial analysis."""
    iteration = state.get("iteration_count", 0)

    messages = [
        SystemMessage(content=f"""You are a CFO / VC partner reviewing a startup financial viability assessment.
This is iteration {iteration} of {MAX_ITERATIONS}.

## Evaluation checklist — score each 1-5 mentally before deciding:
1. **Revenue model clarity** — Are pricing and monetization strategies specific, not vague?
2. **Unit economics** — Are CAC, LTV, margins estimated with stated assumptions?
3. **Cost completeness** — Does the burn rate account for all major categories
   (team, infra, marketing, legal, compliance)?
4. **Realism** — Are projections grounded in comparable startup data, or wishful thinking?
5. **Risk coverage** — Are financial risks identified with severity levels?

## Decision rules
- **Iteration 1**: Be thorough. If unit economics are missing or the cost structure has obvious
  gaps, set status to "NEEDS_MORE_WORK" with specific items to address.
- **Iteration 2**: Be pragmatic. If the analysis has reasonable estimates with stated assumptions
  and covers the key areas, set status to "APPROVED".
- **Iteration 3+**: You MUST set status to "APPROVED". Note limitations as caveats in feedback.

Set `status` to "APPROVED" or "NEEDS_MORE_WORK".
Set `feedback` to specific financial concerns or confirmation of thoroughness."""),
        HumanMessage(content=f"""Startup Idea: {state['startup_idea']}

Financial Analysis:
{state.get('analyst_output', '')}
"""),
    ]

    structured_llm = llm.with_structured_output(ValidatorDecision)
    decision = structured_llm.invoke(messages)

    return {
        **state,
        "validator_feedback": decision.feedback,
        "validator_status": decision.status,
    }


def financial_report_node(state: FinancialState) -> FinancialState:
    """Generates final financial report."""
    messages = [
        SystemMessage(content="""You are a CFO producing a financial viability brief for investors and founders.
Transform the analyst's work into a polished, decision-ready report.

## Required sections (use these exact markdown headings)
### Executive Summary
2-3 sentences: Is this financially viable? What's the biggest financial bet?

### Revenue Model
- Recommended monetization strategy with pricing approach
- Why this model fits the product and market

### Unit Economics
- CAC, LTV, LTV:CAC ratio, gross margin estimates
- Key assumptions stated explicitly

### Capital Requirements & Burn Rate
- Pre-launch funding needed
- Monthly burn rate projection

### Path to Profitability
- Breakeven point (users/revenue)
- Realistic timeline

### Funding Roadmap
- Recommended stages and amounts

### Key Financial Risks
- Top 3-5 risks with severity

### Financial Verdict
One paragraph: Rate as STRONG / VIABLE / MARGINAL / NOT VIABLE.
Explain the primary financial constraint or opportunity.

## Rules
- Keep the total report under 600 words.
- Do not invent numbers not present in the analysis.
- State assumptions and limitations clearly."""),
        HumanMessage(content=f"""Startup Idea: {state['startup_idea']}

Analyst's Work:
{state.get('analyst_output', '')}

Validator Comments:
{state.get('validator_feedback', '')}
"""),
    ]

    response = llm.invoke(messages)
    return {**state, "final_report": response.content.strip()}


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def financial_should_continue(state: FinancialState) -> str:
    """Route: loop back to analyst or move to report generator."""
    if state.get("iteration_count", 0) >= MAX_ITERATIONS:
        return "financial_report"
    if state.get("validator_status", "") == "APPROVED":
        return "financial_report"
    return "analyst"


# ---------------------------------------------------------------------------
# Build subgraph
# ---------------------------------------------------------------------------

def build_financial_subgraph() -> StateGraph:
    graph = StateGraph(FinancialState)

    graph.add_node("analyst", analyst_node)
    graph.add_node("financial_validator", financial_validator_node)
    graph.add_node("financial_report", financial_report_node)

    graph.add_edge(START, "analyst")
    graph.add_edge("analyst", "financial_validator")
    graph.add_conditional_edges(
        "financial_validator",
        financial_should_continue,
        {
            "analyst": "analyst",
            "financial_report": "financial_report",
        },
    )
    graph.add_edge("financial_report", END)

    return graph.compile()
