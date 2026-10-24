import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from pydantic import SecretStr

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com/v1",
    api_key=SecretStr(os.getenv("DEEPSEEK_API_KEY") or ""),
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chat(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


g = StateGraph(State)
g.add_node("chat", chat)
g.set_entry_point("chat")
g.add_edge("chat", END)

# ─── 空位 1：让 compile 把存档点挂上 ───
app = g.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    cfg_a: RunnableConfig = {"configurable": {"thread_id": "A"}}
    cfg_b: RunnableConfig = {"configurable": {"thread_id": "B"}}

    # ─── 空位 2：三处 invoke 各要传哪个 cfg？（第二参数）───
    print(
        "轮1(A)：",
        app.invoke(
            {"messages": [{"role": "user", "content": "我叫小林，记住"}]}, cfg_a
        )["messages"][-1].content,
    )
    print(
        "轮2(A)：",
        app.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]}, cfg_a)[
            "messages"
        ][-1].content,
    )
    print(
        "轮1(B)：",
        app.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]}, cfg_b)[
            "messages"
        ][-1].content,
    )

    snap = app.get_state(cfg_a)
    print("next =", snap.next)
    print("metadata =", snap.metadata)
    print("条数 A =", len(snap.values["messages"]))
    print("条数 B =", len(app.get_state(cfg_b).values["messages"]))
