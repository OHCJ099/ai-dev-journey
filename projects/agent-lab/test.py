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
from rag_tool import search_kb
from tools_demo import multiply

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

    resp = llm.bind_tools([multiply, search_kb]).invoke(state["messages"])
    if resp.tool_calls:
        print(f"tool_call: {resp.tool_calls[0]['name']}")
    return {"messages": [resp]}


def should_continue(state: State) -> str:
    last_msg = state["messages"][-1]
    return "tools" if getattr(last_msg, "tool_calls", None) else END


g = StateGraph(State)
g.add_node("agent", agent)
g.add_node(
    "tools",
    ToolNode([multiply, search_kb], handle_tool_errors=True),
)
g.set_entry_point("agent")

g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
g.add_edge("tools", "agent")

app = g.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    cfg_a: RunnableConfig = {"configurable": {"thread_id": "A"}, "recursion_limit": 10}

    while True:
        times = 0
        r = "r" + str(times)
        msg = input("用户：")

        if msg == "exit":
            break
        if msg == "/clean":
            app.update_state(
                cfg_a,
                {"messages": []},  # 把 messages 强行覆盖为空
            )
            print("记忆已清空")
            continue

        r = app.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": msg,
                    }
                ]
            },
            cfg_a,
        )

        print(f"\nAI: {r['messages'][-1].content}\n")
        times += 1

    # 打印这个会话里所有的历史消息
    print("\n====== 历史记录 ======")
    state = app.get_state(cfg_a)
    for m in state.values["messages"]:
        print(f"{m.type}: {m.content}")
