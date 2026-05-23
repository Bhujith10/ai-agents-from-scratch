"""
Market Research Subgraph

Flow:
  START -> market_search -> market_researcher -> market_validator
    (loop back to market_search if NEEDS_MORE_WORK, max 3 iterations)
    -> market_report -> END

The market_search node uses the LLM to generate multiple short, diverse queries
and aggregates Tavily results. This avoids the 400-char query limit and improves
coverage by searching from different angles each iteration.
"""

from dotenv import load_dotenv, find_dotenv
from typing import Literal, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

from state import MarketResearchState
from tools import search

load_dotenv(find_dotenv())

MAX_ITERATIONS = 3

llm = ChatOpenAI(model="gpt-5.4-mini")


class ValidatorDecision(BaseModel):
    status: Literal["APPROVED", "NEEDS_MORE_WORK"]
    feedback: str


class SearchQueries(BaseModel):
    queries: List[str]


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def market_search_node(state: MarketResearchState) -> MarketResearchState:
    """Uses LLM to generate multiple diverse, short search queries and aggregates results."""
    idea = state["startup_idea"]
    feedback = state.get("validator_feedback", "")
    iteration = state.get("iteration_count", 0)

    # Use LLM to generate 3 diverse, short search queries
    if iteration == 0:
        generation_prompt = f"""Generate exactly 3 short web search queries (each under 80 characters) to research
the following startup idea. Each query should cover a DIFFERENT angle:
- Query 1: Market size and growth (TAM, SAM, CAGR)
- Query 2: Competitors and existing players
- Query 3: Industry trends and customer needs

Startup Idea: {idea}"""
    else:
        generation_prompt = f"""Generate exactly 3 short web search queries (each under 80 characters) to fill
specific gaps identified by a validator. Each query should target a DIFFERENT gap.

Startup Idea: {idea}

Validator Feedback (gaps to fill):
{feedback[:500]}"""

    structured_llm = llm.with_structured_output(SearchQueries)
    query_result = structured_llm.invoke([
        SystemMessage(content="You generate concise, targeted web search queries. Each query must be under 80 characters. Return exactly 3 queries."),
        HumanMessage(content=generation_prompt),
    ])

    # Run each query and aggregate results
    all_results = []
    for i, query in enumerate(query_result.queries[:3], 1):
        # Safety: truncate to 400 chars max (Tavily limit)
        truncated_query = query[:400]
        try:
            result = search(truncated_query)
            all_results.append(f"### Search {i}: \"{truncated_query}\"\n{result}")
        except Exception as e:
            all_results.append(f"### Search {i}: \"{truncated_query}\"\n[Error: {str(e)}]")

    aggregated = "\n\n".join(all_results)
    return {**state, "search_results": aggregated}


def market_researcher_node(state: MarketResearchState) -> MarketResearchState:
    """Analyzes search results to produce structured market research notes."""
    idea = state["startup_idea"]
    feedback = state.get("validator_feedback", "")
    previous_research = state.get("research_output", "")
    iteration = state.get("iteration_count", 0)
    search_results = state.get("search_results", "")

    # Build context for follow-up iterations
    prior_context = ""
    if previous_research:
        prior_context = f"""\n\n## Previous Research (from iteration {iteration})
{previous_research}

## Validator Feedback (address these gaps)
{feedback}"""

    messages = [
        SystemMessage(content="""You are a senior market research analyst at a top-tier consulting firm.
Your job is to produce rigorous, data-backed research notes for a startup validation exercise.

## Required coverage
1. **Total Addressable Market (TAM)** — cite specific dollar figures or user counts with sources
2. **Serviceable Addressable Market (SAM)** — narrow to the startup's realistic segment
3. **Growth trajectory** — CAGR or year-over-year growth rates
4. **Key industry trends** — at least 3 trends shaping this space
5. **Competitive landscape** — name specific companies, their funding, positioning, and weaknesses
6. **Market gaps & white space** — where existing players fall short
7. **Target customer profile** — who would pay for this and why

## Rules
- Prioritize the web search results provided — they are real-time and factual.
- You may supplement with well-established background knowledge, but prefix those points with [Background].
- If data is unavailable for any section, explicitly state "Data not found" rather than guessing.
- Never fabricate statistics, funding amounts, or company names.
- Use bullet points grouped by sub-topic. Be concise but specific.

## If this is a follow-up iteration
- You will see previous research and validator feedback below.
- DO NOT start from scratch. Build on the previous research.
- Focus specifically on filling the gaps the validator identified.
- Merge new findings into the existing research seamlessly."""),
        HumanMessage(content=f"Startup Idea: {idea}\n\nWeb Search Results:\n{search_results}{prior_context}"),
    ]

    response = llm.invoke(messages)
    return {
        **state,
        "research_output": response.content.strip(),
        "iteration_count": iteration + 1,
    }


def market_validator_node(state: MarketResearchState) -> MarketResearchState:
    """Validates market research quality, may request more research."""
    iteration = state.get("iteration_count", 0)

    messages = [
        SystemMessage(content=f"""You are a critical market research validator reviewing research for a startup
validation exercise. This is iteration {iteration} of {MAX_ITERATIONS}.

## Evaluation checklist — score each 1-5 mentally before deciding:
1. **Market sizing** — Are TAM/SAM figures cited with sources? (not vague "large market")
2. **Competitive analysis** — Are specific competitors named with details (funding, users, positioning)?
3. **Trend identification** — Are at least 3 concrete, relevant trends described?
4. **Data quality** — Are claims backed by search results, not generic filler?
5. **Gaps & opportunities** — Is there a clear articulation of where the startup fits?

## Decision rules
- **Iteration 1**: Be thorough. If any checklist item scores below 3, set status to "NEEDS_MORE_WORK".
  Provide specific, actionable feedback listing exactly what data points are missing.
- **Iteration 2**: Be pragmatic. If most items score 3+ and the research is usable for a report,
  set status to "APPROVED". Only reject if there are critical gaps.
- **Iteration 3+**: You MUST set status to "APPROVED" — this is the final iteration.
  Provide a summary of remaining limitations in the feedback field instead.

Set `status` to "APPROVED" or "NEEDS_MORE_WORK".
Set `feedback` to your detailed reasoning and specific gaps (if any)."""),
        HumanMessage(content=f"""Startup Idea: {state['startup_idea']}

Research Output:
{state.get('research_output', '')}
"""),
    ]

    structured_llm = llm.with_structured_output(ValidatorDecision)
    decision = structured_llm.invoke(messages)

    return {
        **state,
        "validator_feedback": decision.feedback,
        "validator_status": decision.status,
    }


def market_report_node(state: MarketResearchState) -> MarketResearchState:
    """Generates final market research report."""
    messages = [
        SystemMessage(content="""You are a senior consultant producing a market research brief for investors.
Transform the raw research notes into a polished, concise report.

## Required sections (use these exact markdown headings)
### Executive Summary
2-3 sentences capturing the market opportunity and key risk.

### Market Size & Growth
- TAM, SAM with figures
- Growth rate / trajectory

### Competitive Landscape
- Table or list of top competitors with positioning
- Key differentiators of the proposed startup

### Key Trends & Tailwinds
- 3-5 trends that favor this startup

### Risks & Headwinds
- Market-specific risks (saturation, regulation, timing)

### Market Verdict
One paragraph: Is the market attractive for this startup? Rate as
STRONG / MODERATE / WEAK opportunity with reasoning.

## Rules
- Keep the total report under 600 words.
- Do not invent data not present in the research notes.
- If data was missing, note it as a limitation."""),
        HumanMessage(content=f"""Startup Idea: {state['startup_idea']}

Research Notes:
{state.get('research_output', '')}

Validator Comments:
{state.get('validator_feedback', '')}
"""),
    ]

    response = llm.invoke(messages)
    return {**state, "final_report": response.content.strip()}


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

def market_should_continue(state: MarketResearchState) -> str:
    """Route: loop back to search node (new queries) or move to report generator."""
    if state.get("iteration_count", 0) >= MAX_ITERATIONS:
        return "market_report"
    if state.get("validator_status", "") == "APPROVED":
        return "market_report"
    return "market_search"


# ---------------------------------------------------------------------------
# Build subgraph
# ---------------------------------------------------------------------------

def build_market_research_subgraph() -> StateGraph:
    graph = StateGraph(MarketResearchState)

    graph.add_node("market_search", market_search_node)
    graph.add_node("market_researcher", market_researcher_node)
    graph.add_node("market_validator", market_validator_node)
    graph.add_node("market_report", market_report_node)

    graph.add_edge(START, "market_search")
    graph.add_edge("market_search", "market_researcher")
    graph.add_edge("market_researcher", "market_validator")
    graph.add_conditional_edges(
        "market_validator",
        market_should_continue,
        {
            "market_search": "market_search",
            "market_report": "market_report",
        },
    )
    graph.add_edge("market_report", END)

    return graph.compile()
