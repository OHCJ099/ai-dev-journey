from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from tools_demo import divide, multiply


class State(TypedDict):
    messages: Annotated[list, add_messages]


def run(handle: bool, name: str, args: dict) -> dict:
    fake = AIMessage(
        content="",
        tool_calls=[
            {"name": name, "args": args, "id": "call_001", "type": "tool_call"}
        ],
    )

    def fake_agent(state: State):  # 假 agent：不调模型，直接吐造好的 AIMessage
        return {"messages": [fake]}

    g = StateGraph(State)
    g.add_node("agent", fake_agent)
    g.add_node("tools", ToolNode([multiply, divide], handle_tool_errors=handle))
    g.set_entry_point("agent")
    g.add_conditional_edges("agent", lambda s: "tools", {"tools": "tools"})
    g.add_edge("tools", END)
    return g.compile().invoke({"messages": []})


# 业务异常


for m in run(True, "nope", {})["messages"]:
    print(type(m).__name__)
    print("  content =", repr(m.content))
    print("  status  =", getattr(m, "status", "无此字段"))
    print("  tool_call_id =", getattr(m, "tool_call_id", "无"))

for m in run(True, "multiply", {"a": 12, "b": 8})["messages"]:  # 正常
    print(type(m).__name__)
    print("  content =", repr(m.content))
    print("  status  =", getattr(m, "status", "无此字段"))
    print("  tool_call_id =", getattr(m, "tool_call_id", "无"))

for m in run(True, "divide", {"a": 96, "b": 0})["messages"]:
    print(type(m).__name__)
    print("  content =", repr(m.content))
    print("  status  =", getattr(m, "status", "无此字段"))
    print("  tool_call_id =", getattr(m, "tool_call_id", "无"))
