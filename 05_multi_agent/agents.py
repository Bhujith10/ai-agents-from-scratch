"""
LangGraph Content Pipeline — Nodes
Nodes: supervisor, researcher, writer, editor, seo_writer
State: ContentState
"""

from dotenv import load_dotenv, find_dotenv
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from state import ContentState
from tools import search

load_dotenv(find_dotenv())


# ---------------------------------------------------------------------------
# Shared LLM
# ---------------------------------------------------------------------------

llm = ChatOpenAI(model="gpt-5.4-mini")


# ---------------------------------------------------------------------------
# 1. Supervisor Node
# ---------------------------------------------------------------------------

class NextStep(BaseModel):
    agent: Literal["researcher", "writer", "editor", "seo_writer", "finish"]
    reasoning: str

SUPERVISOR_SYSTEM = """
You are a content pipeline supervisor. Your job is to route work to the right
agent based on the current pipeline state.

## Available agents
- researcher — gathers facts from the web
- writer     — drafts or revises the blog post
- editor     — reviews the draft and approves or requests changes
- seo_writer — generates SEO metadata for the final post
- finish     — pipeline is complete, stop here

## Routing rules (follow strictly)
1. If research is not done → researcher
2. If research is done but no draft → writer
3. If draft exists but editor has not reviewed → editor
4. If editor feedback exists AND final_post is empty → writer (revision needed)
5. If final_post exists but SEO is not done → seo_writer
6. If SEO is done → finish
7. If iteration_count >= 3, skip further editor/writer cycles and go to
   seo_writer (to prevent infinite loops).
8. If research exists but seems insufficient for the topic (too shallow or
   missing key angles), you may route back to researcher for deeper research.
   However, research_count must be < 3 — if it is already 3, move on to writer.

Set the `agent` field to the next agent name.
Set the `reasoning` field to a brief explanation of why you chose that agent.
"""

def supervisor_node(state: ContentState) -> ContentState:
    """
    Decides which agent should act next.
    Updates `current_agent` in the state.
    """
    messages = [
        SystemMessage(content=SUPERVISOR_SYSTEM),
        HumanMessage(content=f"""
Topic: {state['topic']}

Current pipeline state:
- Research done: {'Yes' if state.get('research') else 'No'}
- Draft written: {'Yes' if state.get('draft') else 'No'}
- Editor feedback given: {'Yes' if state.get('editor_feedback') else 'No'}
- SEO output done: {'Yes' if state.get('seo_output') else 'No'}
- Iteration count: {state.get('iteration_count', 0)}
- Research count: {state.get('research_count', 0)}

Who should act next?
"""),
    ]

    structured_llm = llm.with_structured_output(NextStep)
    result = structured_llm.invoke(messages)

    return {**state, "current_agent": result.agent}


# ---------------------------------------------------------------------------
# 2. Researcher Node  (uses Tavily)
# ---------------------------------------------------------------------------

def researcher_node(state: ContentState) -> ContentState:
    """
    Searches the web for information on the topic using Tavily,
    then summarises the findings into structured research notes.
    """
    topic = state["topic"]

    # --- Search the web first ---
    snippets = search(topic)

    # --- Summarise with LLM ---
    messages = [
        SystemMessage(content="""
You are a research assistant. Your job is to produce concise, well-structured
research notes that a blog writer can use directly.

## How to use information sources

1. **Primary source (highest weight):** The web search results provided below.
   These are real-time and factual — always prioritize them.
2. **Secondary source (supplementary):** Your own training knowledge.
   You may add well-established background context, definitions, or historical
   facts that complement the search results — but ONLY if you are confident
   they are accurate and widely accepted.

## Strict rules
- If the topic is recent, trending, or outside your training data, rely
  EXCLUSIVELY on the search results. Do NOT guess or fill gaps with uncertain
  information.
- Never fabricate statistics, quotes, dates, or claims.
- Clearly distinguish search-sourced facts from your own knowledge by
  prefixing supplementary points with "[Background]".
- If the search results are thin or inconclusive, say so explicitly rather
  than padding with speculation.

## Output format
Clean markdown bullet points grouped by sub-topic.
Include key facts, statistics, perspectives, and relevant examples.
"""),
        HumanMessage(content=f"Topic: {topic}\n\nRaw search results:\n{snippets}"),
    ]

    response = llm.invoke(messages)

    return {
        **state,
        "research": response.content.strip(),
        "research_count": state.get("research_count", 0) + 1,
    }


# ---------------------------------------------------------------------------
# 3. Writer Node
# ---------------------------------------------------------------------------

WRITER_SYSTEM = """
You are an expert blog writer.

Guidelines:
- Use an engaging introduction with a hook.
- Organise the body with clear H2/H3 headings.
- Write in an informative yet conversational tone.
- Include a strong conclusion with a call-to-action.
- Aim for 800–1200 words.
- Output clean markdown.
- Only use facts from the research notes. Do not invent claims or statistics.

## If this is a REVISION (editor feedback is provided)
- Focus specifically on addressing every point in the editor feedback.
- Preserve the parts of the previous draft that were good.
- Do NOT rewrite from scratch — make targeted improvements.
- After addressing feedback, briefly note at the end what you changed
  (wrap in <!-- revision notes: ... --> so it's hidden in final output).
"""

def writer_node(state: ContentState) -> ContentState:
    """
    Writes a full blog post draft from the research notes.
    If editor feedback exists (re-draft scenario), incorporates it.
    """
    feedback_section = ""
    if state.get("editor_feedback"):
        feedback_section = f"""
Editor feedback from the previous draft (please address all points):
{state['editor_feedback']}
"""

    messages = [
        SystemMessage(content=WRITER_SYSTEM),
        HumanMessage(content=f"""
Topic: {state['topic']}

Research Notes:
{state.get('research', 'No research available.')}
{feedback_section}

Write the blog post now.
"""),
    ]

    response = llm.invoke(messages)

    return {
        **state,
        "draft": response.content.strip(),
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


# ---------------------------------------------------------------------------
# 4. Editor / Reviewer Node
# ---------------------------------------------------------------------------

class Feedback(BaseModel):
    status: Literal["APPROVED", "NEEDS_IMPROVEMENT"]
    review: str

EDITOR_SYSTEM = """
You are a senior content editor and reviewer. Your job is to critically review
a blog post draft and provide actionable, specific feedback.

Evaluate the draft on:
1. Clarity and readability
2. Structure and flow
3. Factual accuracy relative to the research
4. Tone and audience fit
5. Grammar and style
6. Completeness and depth

## Approval calibration
- On iteration 1: Be thorough. Request improvements for anything that isn't
  publication-quality. Set status to "NEEDS_IMPROVEMENT" with specific fixes.
- On iteration 2+: Be pragmatic. If the writer addressed your previous
  feedback and the post is at least 80% publication-ready, set status to
  "APPROVED". Don't nitpick endlessly.
- Always provide your reasoning in the review field, even if approving.

Set status to "APPROVED" if the draft is publication-ready.
Set status to "NEEDS_IMPROVEMENT" if changes are needed.
"""

def editor_node(state: ContentState) -> ContentState:
    """
    Reviews the draft and either approves it or returns feedback.
    Stores feedback in `editor_feedback`.
    If approved, copies the draft to `final_post`.
    """
    iteration = state.get('iteration_count', 1)

    messages = [
        SystemMessage(content=EDITOR_SYSTEM),
        HumanMessage(content=f"""
Topic: {state['topic']}
Iteration: {iteration}

Research Notes (for fact-checking):
{state.get('research', '')}

Draft to review:
{state.get('draft', '')}
"""),
    ]

    structured_llm = llm.with_structured_output(Feedback)
    feedback = structured_llm.invoke(messages)

    if feedback.status == "APPROVED":
        return {
            **state,
            "editor_feedback": feedback.review,
            "final_post": state["draft"],
        }

    return {**state, "editor_feedback": feedback.review}


# ---------------------------------------------------------------------------
# 5. SEO Keywords Writer Node
# ---------------------------------------------------------------------------

SEO_SYSTEM = """
You are an SEO specialist. Given a blog post, produce a complete SEO package.

Your output must include:
1. **Primary Keyword** — the single most important keyword phrase
2. **Secondary Keywords** — 5 to 8 supporting keyword phrases
3. **Long-tail Keywords** — 5 conversational / question-based phrases
4. **Meta Title** — ≤60 characters, includes primary keyword
5. **Meta Description** — ≤160 characters, compelling and keyword-rich
6. **Suggested URL Slug** — lowercase, hyphenated, keyword-focused
7. **Content Tags** — 5 tags suitable for a CMS

Format the output as clean markdown with these exact headings.
"""

def seo_writer_node(state: ContentState) -> ContentState:
    """
    Generates SEO keywords, meta tags, and related content for the final post.
    """
    post = state.get("final_post") or state.get("draft", "")

    messages = [
        SystemMessage(content=SEO_SYSTEM),
        HumanMessage(content=f"""
Topic: {state['topic']}

Blog Post:
{post}
"""),
    ]

    response = llm.invoke(messages)

    return {**state, "seo_output": response.content.strip()}


# ---------------------------------------------------------------------------
# Quick smoke-test (optional — remove before production)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    initial_state: ContentState = {
        "topic": "The impact of AI agents on software development in 2025",
        "research": "",
        "draft": "",
        "editor_feedback": "",
        "seo_output": "",
        "current_agent": "",
        "iteration_count": 0,
        "final_post": "",
    }

    print("=== SUPERVISOR ===")
    state = supervisor_node(initial_state)
    print("Next agent:", state["current_agent"])

    print("\n=== RESEARCHER ===")
    state = researcher_node(state)
    print(state["research"][:500], "...")

    print("\n=== WRITER ===")
    state = writer_node(state)
    print(state["draft"][:500], "...")

    print("\n=== EDITOR ===")
    state = editor_node(state)
    print("Feedback:", state["editor_feedback"][:300])

    print("\n=== SEO WRITER ===")
    state = seo_writer_node(state)
    print(state["seo_output"])