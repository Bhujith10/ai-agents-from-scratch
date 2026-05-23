"""
Hierarchical Agent Teams — Startup Idea Validator (Main Graph)

Orchestrates three subgraph teams in parallel, then synthesizes a final report.

Main graph:
  START -> market_research (subgraph)
  START -> technical_feasibility (subgraph)
  START -> financial_analysis (subgraph)
  [all three] -> report_generator -> END
"""

from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from state import OverallState
from market_research import build_market_research_subgraph
from technical_feasibility import build_technical_feasibility_subgraph
from financial import build_financial_subgraph

load_dotenv(find_dotenv())

llm = ChatOpenAI(model="gpt-5.4-mini")

# Pre-compile subgraphs once at module level (avoids recompilation per run)
_market_research_graph = build_market_research_subgraph()
_technical_feasibility_graph = build_technical_feasibility_subgraph()
_financial_graph = build_financial_subgraph()


# ===========================================================================
# Subgraph runner nodes
# ===========================================================================

def run_market_research(state: OverallState) -> OverallState:
    """Runs the market research subgraph."""
    result = _market_research_graph.invoke({
        "startup_idea": state["startup_idea"],
        "search_results": "",
        "research_output": "",
        "validator_feedback": "",
        "validator_status": "",
        "final_report": "",
        "iteration_count": 0,
    })
    return {"market_research_report": result["final_report"]}


def run_technical_feasibility(state: OverallState) -> OverallState:
    """Runs the technical feasibility subgraph."""
    result = _technical_feasibility_graph.invoke({
        "startup_idea": state["startup_idea"],
        "engineer_output": "",
        "validator_feedback": "",
        "validator_status": "",
        "final_report": "",
        "iteration_count": 0,
    })
    return {"technical_feasibility_report": result["final_report"]}


def run_financial_analysis(state: OverallState) -> OverallState:
    """Runs the financial analysis subgraph."""
    result = _financial_graph.invoke({
        "startup_idea": state["startup_idea"],
        "analyst_output": "",
        "validator_feedback": "",
        "validator_status": "",
        "final_report": "",
        "iteration_count": 0,
    })
    return {"financial_report": result["final_report"]}


# ===========================================================================
# Final report generator node
# ===========================================================================

def final_report_generator(state: OverallState) -> OverallState:
    """Combines all three team reports into a final startup validation report."""
    messages = [
        SystemMessage(content="""You are a managing partner at a top-tier startup accelerator.
You have received three independent analysis reports on a startup idea. Your job is to
synthesize them into a single, investor-grade validation report.

## Required sections (use these exact markdown headings)

# Startup Validation Report

## Executive Summary
3-4 sentences. What is the idea? Is it worth pursuing? What's the single biggest risk?

## Market Opportunity
Synthesize the market research team's findings:
- Market size and growth potential
- Competitive positioning
- Market verdict (from their report)

## Technical Feasibility
Synthesize the engineering team's findings:
- Architecture viability
- Key technical risks
- Technical verdict (from their report)

## Financial Viability
Synthesize the financial team's findings:
- Revenue model and unit economics
- Capital requirements
- Financial verdict (from their report)

## Overall Recommendation
Choose ONE and bold it: **GO** / **CONDITIONAL GO** / **NO-GO**

Provide 2-3 sentences of reasoning that weighs all three dimensions.
For CONDITIONAL GO, list the specific conditions that must be met.

## Confidence Score
Rate your confidence in this recommendation: LOW / MEDIUM / HIGH.
Explain what additional information would increase confidence.

## Next Steps
If GO or CONDITIONAL GO, list 5-7 specific, prioritized action items with owners
(e.g., "Founders: Validate pricing with 20 target customer interviews").

## Critical Risks
Top 3 risks that could kill this startup, each with:
- Description
- Likelihood: Low / Medium / High
- Impact: Low / Medium / High
- Mitigation strategy

## Rules
- Do NOT invent findings not present in the team reports.
- If any team report was thin or had noted limitations, flag that in your synthesis.
- Be direct and honest. Sugarcoating helps no one.
- Keep the total report under 1000 words."""),
        HumanMessage(content=f"""Startup Idea: {state['startup_idea']}

=== MARKET RESEARCH REPORT ===
{state.get('market_research_report', 'Not available')}

=== TECHNICAL FEASIBILITY REPORT ===
{state.get('technical_feasibility_report', 'Not available')}

=== FINANCIAL VIABILITY REPORT ===
{state.get('financial_report', 'Not available')}
"""),
    ]

    response = llm.invoke(messages)
    return {**state, "final_report": response.content.strip()}


def build_main_graph() -> StateGraph:
    """
    Main graph that runs all three subgraphs in parallel,
    then combines results in a final report generator.
    """
    graph = StateGraph(OverallState)

    # Register nodes
    graph.add_node("market_research", run_market_research)
    graph.add_node("technical_feasibility", run_technical_feasibility)
    graph.add_node("financial_analysis", run_financial_analysis)
    graph.add_node("report_generator", final_report_generator)

    # Fan-out: START -> all three teams
    graph.add_edge(START, "market_research")
    graph.add_edge(START, "technical_feasibility")
    graph.add_edge(START, "financial_analysis")

    # Fan-in: all three teams -> report_generator
    graph.add_edge("market_research", "report_generator")
    graph.add_edge("technical_feasibility", "report_generator")
    graph.add_edge("financial_analysis", "report_generator")

    # report_generator -> END
    graph.add_edge("report_generator", END)

    return graph.compile()
