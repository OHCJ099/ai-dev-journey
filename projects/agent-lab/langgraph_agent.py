import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
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
    error_count = 0
    for msg in reversed(state["messages"]):
        status = getattr(msg, "status", None)
        if status == "error":
            error_count += 1
        elif status == "success":
            break

    if error_count >= 3:
        return {
            "messages": [AIMessage(content="系统连续报错达到 3 次，已强制终止任务。")]
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

app = g.compile()
