# graph_builder.py
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage
import config

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    turn_counter: int

# NEW: The function now accepts an optional 'internal_turn_limit'
def create_agent_workflow(llm, tools, internal_turn_limit: int = None):
    """Creates a compiled LangGraph agent workflow."""
    model_with_tools = llm.bind_tools(tools)
    
    # Use the specific internal limit if provided, otherwise use the main config
    max_turns = internal_turn_limit if internal_turn_limit is not None else config.MAX_TURNS

    def call_model(state: AgentState):
        turn = state.get("turn_counter", 0) + 1
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response], "turn_counter": turn}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            # The check now uses our 'max_turns' variable
            if state.get("turn_counter", 0) >= max_turns:
                return END
            return "call_tool"
        return END

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("call_tool", ToolNode(tools))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("call_tool", "agent")

    return workflow.compile()