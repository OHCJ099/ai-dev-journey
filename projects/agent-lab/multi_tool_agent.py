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
    model=os.getenv("DEEPSEEK_MODEL") or "deepseek-v4.1-flash-cn",
    base_url=os.getenv("DEEPSEEK_BASE_URL") or "http://127.0.0.1:8787/v1",
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
    print(f"[agent] 返回 tool_calls={resp.tool_calls}")
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

    r1 = app.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "查一下年假有几天，然后算一下如果我有 3 天没休，能折算多少钱，每天 300 元",
                }
            ]
        },
        cfg_a,
    )
    # 打印这个会话里所有的历史消息
    print("\n====== 历史记录 ======")
    state = app.get_state(cfg_a)
    for m in state.values["messages"]:
        print(f"{m.type}: {m.content}")
