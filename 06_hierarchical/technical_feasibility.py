"""
Technical Feasibility Subgraph

Flow:
  START -> engineer -> technical_validator
    (loop back to engineer if NEEDS_MORE_WORK, max 3 iterations)
    -> technical_report -> END
"""

from dotenv import load_dotenv, find_dotenv
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from state import TechnicalFeasibilityState

load_dotenv(find_dotenv())

MAX_ITERATIONS = 3

llm = ChatOpenAI(model="gpt-5.4-mini")


class ValidatorDecision(BaseModel):
    status: Literal["APPROVED", "NEEDS_MORE_WORK"]
    feedback: str


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def engineer_node(state: TechnicalFeasibilityState) -> TechnicalFeasibilityState:
    """Analyzes technical feasibility of the startup idea."""
    idea = state["startup_idea"]
    feedback = state.get("validator_feedback", "")
    previous_output = state.get("engineer_output", "")
    iteration = state.get("iteration_count", 0)

    prior_context = ""
    if previous_output:
        prior_context = f"""\n\n## Previous Analysis (iteration {iteration})
{previous_output}

## Validator Feedback (address these concerns specifically)
{feedback}"""

    messages = [
        SystemMessage(content="""You are a principal engineer and CTO-level technical advisor.
Perform a rigorous technical feasibility assessment for the given startup idea.

## Required analysis (use these sections)
1. **Architecture Overview** — High-level system design. What are the core components?
   (backend, frontend, data pipeline, ML models, third-party integrations, etc.)
2. **Technology Stack** — Specific recommendations (languages, frameworks, databases, cloud
   services). Justify each choice briefly.
3. **Complexity Rating** — Rate as LOW / MEDIUM / HIGH / VERY HIGH.
   Break down: what parts are standard engineering vs. genuinely hard problems?
4. **Scalability Plan** — How does the system handle 10x and 100x growth?
   Identify bottlenecks early.
5. **Technical Risks** — List each risk with severity (Critical/High/Medium/Low) and
   a mitigation strategy. Consider: data privacy, security, API dependencies,
   model accuracy (if ML), regulatory/compliance tech requirements.
6. **Team Requirements** — Minimum viable engineering team (roles + seniority).
7. **Development Timeline** — Phase-based estimate (MVP, Beta, V1) with rough durations.
   Be honest — don't underestimate.
8. **Build vs. Buy Decisions** — What should be built in-house vs. using existing services?

## Rules
- Be realistic and critical. Optimistic hand-waving helps no one.
- If a core technical component relies on unproven or cutting-edge tech, flag it explicitly.
- If this is a follow-up iteration, DO NOT rewrite from scratch. Refine your previous analysis
  by addressing the validator's specific concerns. Preserve what was already strong."""),
        HumanMessage(content=f"Startup Idea: {idea}{prior_context}"),
    ]

    response = llm.invoke(messages)
    return {
        **state,
        "engineer_output": response.content.strip(),
        "iteration_count": iteration + 1,
    }


def technical_validator_node(state: TechnicalFeasibilityState) -> TechnicalFeasibilityState:
    """Critically validates the engineer's analysis."""
    iteration = state.get("iteration_count", 0)

    messages = [
        SystemMessage(content=f"""You are a VP of Engineering reviewing a technical feasibility assessment.
This is iteration {iteration} of {MAX_ITERATIONS}.

## Evaluation checklist — score each 1-5 mentally before deciding:
1. **Architecture completeness** — Are all major components identified? Any missing pieces?
2. **Risk identification** — Are security, privacy, compliance, and scaling risks covered?
3. **Timeline realism** — Is the estimate honest or suspiciously optimistic?
4. **Technology choices** — Are the stack decisions justified and appropriate?
5. **Blind spots** — Did the engineer miss anything critical (DevOps, monitoring, data migration,
   regulatory tech requirements)?

## Decision rules
- **Iteration 1**: Be thorough. If critical risks are missing or the architecture has gaps,
  set status to "NEEDS_MORE_WORK" with specific technical questions to address.
- **Iteration 2**: Be pragmatic. If the analysis covers the essentials and risks are identified,
  set status to "APPROVED" even if minor details could be better.
- **Iteration 3+**: You MUST set status to "APPROVED". Note any remaining concerns in feedback
  as caveats rather than blockers.

Set `status` to "APPROVED" or "NEEDS_MORE_WORK".
Set `feedback` to specific technical concerns or confirmation of thoroughness."""),
        HumanMessage(content=f"""Startup Idea: {state['startup_idea']}

Engineer's Analysis:
{state.get('engineer_output', '')}
"""),
    ]

    structured_llm = llm.with_structured_output(ValidatorDecision)
    decision = structured_llm.invoke(messages)

    return {
        **state,
        "validator_feedback": decision.feedback,
        "validator_status": decision.status,
    }


def technical_report_node(state: TechnicalFeasibilityState) -> TechnicalFeasibilityState:
    """Generates final technical feasibility report."""
    messages = [
        SystemMessage(content="""You are a CTO producing a technical feasibility brief for stakeholders.
Transform the engineer's analysis into a polished, decision-ready report.

## Required sections (use these exact markdown headings)
### Executive Summary
2-3 sentences: Is this technically buildable? What's the biggest technical bet?

### Recommended Architecture
- High-level component diagram description
- Key technology choices with brief justification

### Complexity & Timeline
- Complexity rating: LOW / MEDIUM / HIGH / VERY HIGH
- Phase-based timeline (MVP → Beta → V1)

### Key Risks & Mitigations
- Top 3-5 risks, each with severity and mitigation plan

### Team Requirements
- Minimum viable team composition

### Technical Verdict
One paragraph: Rate as FEASIBLE / FEASIBLE WITH CAVEATS / HIGH RISK / NOT FEASIBLE.
Explain the primary technical constraint.

## Rules
- Keep the total report under 600 words.
- Be direct and actionable. No filler."""),
        HumanMessage(content=f"""Startup Idea: {state['startup_idea']}

Engineer's Analysis:
{state.get('engineer_output', '')}

Validator Comments:
{state.get('validator_feedback', '')}
"""),
    ]

    response = llm.invoke(messages)
    return {**state, "final_report": response.content.strip()}


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def technical_should_continue(state: TechnicalFeasibilityState) -> str:
    """Route: loop back to engineer or move to report generator."""
    if state.get("iteration_count", 0) >= MAX_ITERATIONS:
        return "technical_report"
    if state.get("validator_status", "") == "APPROVED":
        return "technical_report"
    return "engineer"


# ---------------------------------------------------------------------------
# Build subgraph
# ---------------------------------------------------------------------------

def build_technical_feasibility_subgraph() -> StateGraph:
    graph = StateGraph(TechnicalFeasibilityState)

    graph.add_node("engineer", engineer_node)
    graph.add_node("technical_validator", technical_validator_node)
    graph.add_node("technical_report", technical_report_node)

    graph.add_edge(START, "engineer")
    graph.add_edge("engineer", "technical_validator")
    graph.add_conditional_edges(
        "technical_validator",
        technical_should_continue,
        {
            "engineer": "engineer",
            "technical_report": "technical_report",
        },
    )
    graph.add_edge("technical_report", END)

    return graph.compile()
