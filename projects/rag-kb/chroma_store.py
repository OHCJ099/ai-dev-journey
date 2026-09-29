# projects/rag-kb/chroma_store.py
"""W10 第 4 件：用 Chroma 重做 retriever.py 的检索 —— 对照「框架帮我做了什么」。

跑法（仓库根目录）：uv run python projects/rag-kb/chroma_store.py
"""

from pathlib import Path

import chromadb
from loader import load_documents
from retriever import embed  # 复用你自己写的向量化函数
from splitter import split_text

DATA_DIR = Path(__file__).parent / "data"


def build_collection(chunks: list[str]):
    """把全部块存进 Chroma，返回 collection。"""
    client = chromadb.Client()  # 内存版数据库：每次跑都是全新的，进程退出就没了
    collection = client.create_collection(
        name="zhidu",
        metadata={"hnsw:space": "cosine"},  # 距离按余弦算
    )

    b_ids = []
    b_embed = []
    for i in range(len(chunks)):
        b_ids.append(f"chunk_{i}")

    for chunk in chunks:
        b_embed.append(embed(chunk))

    collection.add(
        ids=b_ids,  # ★ 54 个不重复的字符串编号（提示：循环 + f-string）
        documents=chunks,  # ★ 块文本列表（就是 chunks）
        embeddings=b_embed,  # ★ 54 个向量：循环里每个块过一遍 embed()，append 进列表
    )
    return collection


if __name__ == "__main__":
    docs = load_documents(DATA_DIR)
    chunks = []
    for doc in docs:
        chunks.extend(split_text(doc["text"], 500, 50))

    collection = build_collection(chunks)

    questions = [
        "员工请假的规则是什么？",
        "员工出差乘坐高铁，车票该怎么报销？",
        "发现办公区域有安全隐患，员工应该怎么处理？",
    ]

    for question in questions:
        result = collection.query(query_embeddings=[embed(question)], n_results=3)
        print(f"== {question} ==")

        documents = result["documents"]
        distances = result["distances"]

        if documents is not None and distances is not None:
            for i in range(len(result["ids"][0])):
                print(
                    f"ids: {result['ids'][0][i]}, "
                    f"内容: {documents[0][i][:30]}, "
                    f"距离: {distances[0][i]:.2f}"
                )
