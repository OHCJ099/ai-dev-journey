import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "rag-kb"))

import config
import query_lab
from index_store import open_index
from langchain_core.tools import tool


@tool
def search_kb(question: str) -> str:
    """在制度知识库里检索。输入一个自然语言问题，返回最相关的几段原文。"""
    collection = open_index(config.REAL_INDEX_PATH)
    hits = query_lab.query_index(collection, question)
    parts = []
    for index, hit in enumerate(hits, start=1):
        parts.append(f"[{index}]{hit[0]}：{hit[1]}\n\n")
    return "".join(parts)


if __name__ == "__main__":
    print(search_kb.invoke("年假有几天"))
