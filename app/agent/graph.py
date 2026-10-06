from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agent.state import HRAgentState
from app.agent.llm import get_llm
from app.agent.nodes import create_agent_node
from app.agent.tools import create_hr_tools


def should_continue(state: HRAgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


def create_hr_graph(
    db,
    employee_id: str,
    correlation_id: str,
    conversation_id: str | None = None,
):
    """
    Create and compile the HR LangGraph.

    Phase 9.5:
    correlation_id and conversation_id are passed to the
    HR tools so every tool execution can be audited.
    """

    llm = get_llm()

    tools = create_hr_tools(
        db=db,
        employee_id=employee_id,
        correlation_id=correlation_id,
        conversation_id=conversation_id,
    )

    agent_node = create_agent_node(
        llm,
        tools,
    )

    tool_node = ToolNode(tools)

    graph = StateGraph(HRAgentState)

    graph.add_node(
        "agent",
        agent_node,
    )

    graph.add_node(
        "tools",
        tool_node,
    )

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge(
        "tools",
        "agent",
    )

    return graph.compile()