from typing import TypedDict

from langgraph.graph import END, StateGraph


class State(TypedDict):
    n: int


def agent(state: State):
    print("agent 被调用，读到 n =", state["n"])
    return {"n": state["n"] + 1}


def tools(state: State):
    print("tools 被调用，读到 n =", state["n"])
    return {"n": state["n"] + 10}


def should_continue(state: State):  # ① 一个新函数：只做判断，不干活
    if state["n"] < 5:
        print("  判断：n < 5，回 agent 再来一轮")
        return "回去"
    print("  判断：n >= 5，结束")
    return "结束"


graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("tools", tools)
graph.set_entry_point("agent")
graph.add_edge("agent", "tools")
# ② tools 跑完后不再无条件走，而是把这个函数交给框架问一句"下一步去哪"
graph.add_conditional_edges(
    "tools",
    should_continue,
    {"回去": "agent", "结束": END},  # ③ 字符串 → 真实节点 的对照表
)

app = graph.compile()
out = app.invoke({"n": 0}, {"recursion_limit": 20})
print("最终黑板 =", out)
