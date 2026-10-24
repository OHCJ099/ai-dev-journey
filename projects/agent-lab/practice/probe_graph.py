from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages


class State(TypedDict):  # 黑板：规定有哪几栏
    messages: Annotated[list, add_messages]
    n: int


def agent(state: State):  # 机器 1
    print("[agent] 消息条数 =", len(state["messages"]), " n =", state["n"])
    return {"messages": [{"role": "ai", "content": f"第 {state['n']} 轮"}]}


def tools(state: State):  # 机器 2
    print("[tools] 消息条数 =", len(state["messages"]), " n =", state["n"])
    return {"messages": [{"role": "ai", "content": "工具跑完了"}], "n": state["n"] + 1}


def should_continue(state: State) -> str:  # 岔路口的路牌
    return "tools" if state["n"] < 3 else END


g = StateGraph(State)
g.add_node("agent", agent)
g.add_node("tools", tools)
g.set_entry_point("agent")
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")

app = g.compile()
out = app.invoke({"messages": [{"role": "user", "content": "开始"}], "n": 0})
print("--- 最终消息 ---")
for m in out["messages"]:
    print(" ", m.type, "|", m.content)
