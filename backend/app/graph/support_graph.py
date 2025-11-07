from langgraph.graph import StateGraph, START, END
from app.agents.agents import SalesAgent, TechAgent
from typing import TypedDict, Optional

# Define the state schema
class SupportState(TypedDict):
    context: Optional[str]  
    response: Optional[str]
    next_agent: Optional[str]
    agent: Optional[str]  # who handled the reply: "sales" or "tech"

sales = SalesAgent()
tech = TechAgent()

def sales_node(state: SupportState):
    """
    Sales node:
    - Calls SalesAgent.respond(query, context)
    - If SalesAgent returns the transfer tag, set next_agent="tech", agent=None (or "sales" if you want an explicit tag)
    - Otherwise set next_agent="end" and agent="sales"
    """
    context = state.get("context", None)

    reply = sales.respond(context)
    # Default values
    state["response"] = None
    state["agent"] = None
    state["next_agent"] = "end"

    if "[ACTION: TRANSFER_TO_TECH]" in reply:
        # Sales detected a technical issue — handover to tech.
        state["next_agent"] = "tech_agent"
        state["response"] = (
            "That sounds like a technical issue. Connecting you to a Tech Expert..."
        )
        state["agent"] = "sales_agent"
    else:
        state["response"] = reply
        state["agent"] = "sales_agent"
        state["next_agent"] = "end"

    return state

def tech_node(state: SupportState):
    """
    Tech node:
    - Calls TechAgent.respond(context) and returns final response.
    - Tech always ends.
    """
    context = state.get("context", None)

    reply = tech.respond(context)
    state["response"] = reply
    state["agent"] = "tech_agent"
    state["next_agent"] = "end"
    return state

# --- Build dynamic flow ---
graph = StateGraph(SupportState)

graph.add_node("sales", sales_node)
graph.add_node("tech", tech_node)

graph.add_edge(START, "sales")

# Add conditional logic for branching
graph.add_conditional_edges(
    "sales",
    lambda st: st["next_agent"],  # decide next step dynamically
    {
        "tech_agent": "tech",
        "end": END
    }
)

# Tech always ends
graph.add_edge("tech", END)

support_graph = graph.compile()

