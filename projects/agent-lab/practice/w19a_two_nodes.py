from typing import TypedDict

from langgraph.graph import END, StateGraph


class State(TypedDict):  # ① 黑板：规定能写哪些字段
    n: int


def agent(state: State):  # ② 节点 1：一个普通函数
    print("agent 被调用，读到 n =", state["n"])
    return {"n": state["n"] + 1}  # 只交回要改的字段


def tools(state: State):  # ② 节点 2
    print("tools 被调用，读到 n =", state["n"])
    return {"n": state["n"] + 10}


graph = StateGraph(State)  # ③ 拿黑板建一张空图
graph.add_node("agent", agent)  # ④ 把函数挂成节点（传函数名，不加括号）
graph.add_node("tools", tools)
graph.set_entry_point("agent")  # ⑤ 起点
graph.add_edge("agent", "tools")  # ⑥ 传送带：agent 跑完必去 tools
graph.add_edge("tools", END)  #     tools 跑完结束

app = graph.compile()  # ⑦ 图纸变机器
out = app.invoke({"n": 0})  # ⑧ 塞初始数据，开跑
print("最终黑板 =", out)
