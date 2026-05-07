from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools.structured import StructuredTool
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
import operator
from tools import get_file_tree, get_file_content, search

# ── 1. Define Tools ──────────────────────────────────────────────────────────

search_tool = StructuredTool.from_function(search)
get_file_tree_tool = StructuredTool.from_function(get_file_tree)
get_file_content_tool = StructuredTool.from_function(get_file_content)

tools = [get_file_tree_tool, get_file_content_tool, search_tool]

# ── 2. Define State ───────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # messages accumulate

# ── 3. Define Nodes ───────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-5.4-mini")
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: AgentState):
    """LLM decides: respond or call a tool."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)

# ── 4. Routing Logic ──────────────────────────────────────────────────────────

def should_continue(state: AgentState):
    """If LLM made tool calls → go to tool node, else → end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# ── 5. Build Graph ────────────────────────────────────────────────────────────

def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END}
    )

    graph.add_edge("tools", "agent")  # after tool → back to agent

    return graph


if __name__ == "__main__":
    app = build_graph().compile()
    result = app.invoke({
        "messages": [HumanMessage(content="Fetch the file structure of https://github.com/mem0ai/mem0 and give me a high-level summary.")]
    })
    print(result["messages"][-1].content)