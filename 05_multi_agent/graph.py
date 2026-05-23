"""
LangGraph Content Pipeline — Graph
Wires supervisor, researcher, writer, editor, seo_writer into a StateGraph.

Flow:
  START
    └─> supervisor
          ├─> researcher ──> supervisor
          ├─> writer     ──> supervisor
          ├─> editor     ──> supervisor
          ├─> seo_writer ──> END
          └─> finish ──> END
"""

from langgraph.graph import StateGraph, START, END

from state import ContentState
from agents import (
    supervisor_node,
    researcher_node,
    writer_node,
    editor_node,
    seo_writer_node,
)


# ---------------------------------------------------------------------------
# Routing function — reads current_agent set by supervisor
# ---------------------------------------------------------------------------

MAX_ITERATIONS = 3  # max writer↔editor loops before forcing FINISH

def route_from_supervisor(state: ContentState) -> str:
    """
    Called after every supervisor run.
    Maps state['current_agent'] → next node name (or END).
    Also guards against infinite re-draft loops.
    """
    agent = state.get("current_agent", "").strip().lower()

    # Safety: if writer has looped too many times, force to seo
    if state.get("iteration_count", 0) >= MAX_ITERATIONS and agent == "writer":
        return "seo_writer"

    # Safety: if researcher has looped too many times, force to writer
    if state.get("research_count", 0) >= MAX_ITERATIONS and agent == "researcher":
        return "writer"

    routing_map = {
        "researcher": "researcher",
        "writer":     "writer",
        "editor":     "editor",
        "seo_writer": "seo_writer",
        "finish":     END,
    }

    return routing_map.get(agent, END)  # default to END on unknown


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    graph = StateGraph(ContentState)

    # --- Register nodes ---
    graph.add_node("supervisor",  supervisor_node)
    graph.add_node("researcher",  researcher_node)
    graph.add_node("writer",      writer_node)
    graph.add_node("editor",      editor_node)
    graph.add_node("seo_writer",  seo_writer_node)

    # --- Entry point ---
    graph.add_edge(START, "supervisor")

    # --- Supervisor routes conditionally to any node or END ---
    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "researcher": "researcher",
            "writer":     "writer",
            "editor":     "editor",
            "seo_writer": "seo_writer",
            END:          END,
        },
    )

    # --- Every worker reports back to supervisor after finishing ---
    graph.add_edge("researcher",  "supervisor")
    graph.add_edge("writer",      "supervisor")
    graph.add_edge("editor",      "supervisor")

    # --- SEO is the last step; goes straight to END ---
    graph.add_edge("seo_writer",  END)

    return graph.compile()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = build_graph()

    initial_state: ContentState = {
        "topic": "The impact of AI agents on software development in 2025",
        "research": "",
        "draft": "",
        "editor_feedback": "",
        "seo_output": "",
        "current_agent": "",
        "iteration_count": 0,
        "research_count": 0,
        "final_post": "",
    }

    print("Starting content pipeline...\n")

    # stream() yields state after each node — great for visibility
    final = None
    for step in app.stream(initial_state, {"recursion_limit": 25}):
        node_name = list(step.keys())[0]
        final = step[node_name]
        print(f"[{node_name}] done | current_agent: '{final.get('current_agent', '')}' | iterations: {final.get('iteration_count', 0)}")

    print("\n========== FINAL POST ==========")
    print(final.get("final_post") or final.get("draft"))
    print("\n========== SEO OUTPUT ==========")
    print(final.get("seo_output"))