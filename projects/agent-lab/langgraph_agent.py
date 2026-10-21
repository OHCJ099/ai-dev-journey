import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
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
    resp = llm.bind_tools([multiply, divide, get_weather, count_chars]).invoke(
        state["messages"]
    )
    print(f"[agent] 返回tool_calls={resp.tool_calls}")
    return {"messages": [resp]}


def should_continue(state: State) -> str:
    return "tools" if state["messages"][-1].tool_calls else END


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

out = app.invoke(
    {"messages": [{"role": "user", "content": "12 乘 8 再除以 4"}]},
    {"recursion_limit": 10},
)
