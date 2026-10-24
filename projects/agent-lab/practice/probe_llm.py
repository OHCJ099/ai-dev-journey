import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import SecretStr

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com/v1",
    api_key=SecretStr(os.getenv("DEEPSEEK_API_KEY") or ""),
)


@tool
def multiply(a: float, b: float) -> str:
    """两数相乘"""
    return str(a * b)


@tool
def divide(a: float, b: float) -> str:
    """两数相除"""
    if b == 0:
        raise ValueError("除数不能为 0")
    return str(a / b)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent(state: State):
    resp = llm.bind_tools([multiply, divide]).invoke(state["messages"])
    return {"messages": [resp]}


def should_continue(state: State) -> str:
    return "tools" if state["messages"][-1].tool_calls else END


g = StateGraph(State)
g.add_node("agent", agent)
g.add_node("tools", ToolNode([multiply, divide], handle_tool_errors=True))
g.set_entry_point("agent")

# 条件边：如果模型要调工具，就去 tools；不然就去 END
g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})

# 工具跑完，固定回到 agent 节点
g.add_edge("tools", "agent")

app = g.compile()

out = app.invoke(
    {"messages": [{"role": "user", "content": "12 乘 8 再除以 0"}]},
    {"recursion_limit": 10},
)

print("-" * 80)
for m in out["messages"]:
    # 格式化打印，让你一眼看清 6 条消息
    print(
        f"{m.type:8} | {str(m.content)[:40]:40} | tool_calls={getattr(m, 'tool_calls', None)}"
    )
