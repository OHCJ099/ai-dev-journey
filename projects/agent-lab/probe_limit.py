from typing import TypedDict

from langgraph.graph import StateGraph


class State(TypedDict):
    n: int


def agent(state: State):
    print("agent 第", state["n"] + 1, "步")
    return {"n": state["n"] + 1}


def tools(state: State):
    print("tools 第", state["n"] + 1, "步")
    return {"n": state["n"] + 1}


g = StateGraph(State)
g.add_node("agent", agent)
g.add_node("tools", tools)
g.set_entry_point("agent")
g.add_edge("agent", "tools")
g.add_edge("tools", "agent")

app = g.compile()
app.invoke({"n": 0}, {"recursion_limit": 4})
