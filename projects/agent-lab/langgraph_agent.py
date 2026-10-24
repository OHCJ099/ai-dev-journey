import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import SecretStr
from tools_demo import count_chars, divide, get_weather, multiply

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com/v1",
    api_key=SecretStr(os.getenv("DEEPSEEK_API_KEY") or ""),
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent(state: State):
    fail_counts: dict[str, int] = {}
    for msg in state["messages"]:
        tool_name = getattr(msg, "name", None)
        status = getattr(msg, "status", None)

        if msg.type == "human":
            fail_counts = {}
            continue

        if tool_name is not None:
            if status == "error":
                fail_counts[tool_name] = fail_counts.get(tool_name, 0) + 1
            elif status == "success":
                fail_counts[tool_name] = 0

    if max(fail_counts.values(), default=0) >= 3:
        return {
            "messages": [
                AIMessage(content="系统检测到工具连续报错 3 次，已强制终止任务。")
            ]
        }

    resp = llm.bind_tools([multiply, divide, get_weather, count_chars]).invoke(
        state["messages"]
    )
    print(f"[agent] 返回 tool_calls={resp.tool_calls}")
    return {"messages": [resp]}


def should_continue(state: State) -> str:
    last_msg = state["messages"][-1]
    return "tools" if getattr(last_msg, "tool_calls", None) else END


g = StateGraph(State)
g.add_node("agent", agent)
g.add_node(
    "tools",
    ToolNode([multiply, divide, get_weather, count_chars], handle_tool_errors=True),
)
g.set_entry_point("agent")

g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")

app = g.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    cfg_a: RunnableConfig = {"configurable": {"thread_id": "A"}, "recursion_limit": 10}
    cfg_b: RunnableConfig = {"configurable": {"thread_id": "B"}, "recursion_limit": 10}
    bad: RunnableConfig = {"configurable": {"thread_id": "X", "recursion_limit": 10}}

    # 第一次对话
    print("--- 第一次回答 ---")
    r1 = app.invoke(
        {"messages": [{"role": "user", "content": "12 乘 8 再除以 4 等于多少？"}]},
        cfg_a,
    )
    print(r1["messages"][-1].content)

    # 第二次对话（测试记忆）
    print("\n--- 第二次回答 ---")
    r2 = app.invoke(
        {"messages": [{"role": "user", "content": "刚才那个结果再加 10 是多少？"}]},
        cfg_a,
    )
    print(r2["messages"][-1].content)

    # 打印这个会话里所有的历史消息
    print("\n--- 历史记录 ---")
    state = app.get_state(cfg_a)
    for m in state.values["messages"]:
        print(f"{m.type}: {m.content}")

    print("\n--- 换 thread 问同一句 ---")
    r3 = app.invoke(
        {"messages": [{"role": "user", "content": "刚才那个结果再加 10 是多少？"}]},
        cfg_b,
    )
    print(r3["messages"][-1].content)
    print("A 条数 =", len(app.get_state(cfg_a).values["messages"]))
    print("B 条数 =", len(app.get_state(cfg_b).values["messages"]))
    rx = app.invoke({"messages": [{"role": "user", "content": "1+1"}]}, bad)
    print(rx["messages"][-1].content)
