# projects/rag-kb/chroma_store.py
"""W10 第 4 件：用 Chroma 重做 retriever.py 的检索 —— 对照「框架帮我做了什么」。

跑法（仓库根目录）：uv run python projects/rag-kb/chroma_store.py
"""

from pathlib import Path

import chromadb
from loader import load_documents
from retriever import embed  # 复用你自己写的向量化函数
from splitter import split_text

# 根据脚本自身位置定位制度文档目录。
DATA_DIR = Path(__file__).parent / "data"


def build_collection(chunks: list[str]):
    """把全部块存进 Chroma，返回 collection。"""
    client = chromadb.Client()  # 内存版数据库：每次跑都是全新的，进程退出就没了
    collection = client.create_collection(
        name="zhidu",
        metadata={"hnsw:space": "cosine"},  # 距离按余弦算
    )

    # 文本、编号和向量按相同顺序排列，保证每块数据相互对应。
    b_ids = []
    b_embed = []
    # 为每块生成唯一字符串编号，作为数据库中的标识。
    for i in range(len(chunks)):
        b_ids.append(f"chunk_{i}")

    # 调用向量化服务，逐块得到表示语义的数字列表。
    for chunk in chunks:
        b_embed.append(embed(chunk))

    collection.add(
        ids=b_ids,  # 每块的唯一编号
        documents=chunks,  # 每块的原始文本
        embeddings=b_embed,  # 与文本一一对应的向量
    )
    return collection


# 直接运行时：加载文档、切块、建库，再查询示例问题。
if __name__ == "__main__":
    docs = load_documents(DATA_DIR)
    chunks = []
    for doc in docs:
        # extend 将当前文档的多个块加入同一个总列表。
        chunks.extend(split_text(doc["text"], 500, 50))

    collection = build_collection(chunks)

    questions = [
        "员工请假的规则是什么？",
        "员工出差乘坐高铁，车票该怎么报销？",
        "发现办公区域有安全隐患，员工应该怎么处理？",
    ]

    for question in questions:
        # 问题也转成向量，取距离最近的 3 个文本块。
        result = collection.query(query_embeddings=[embed(question)], n_results=3)
        print(f"== {question} ==")

        # 查询结果按问题分组；这里只有一个问题，因此使用第 0 组。
        documents = result["documents"]
        distances = result["distances"]

        # 确认文本和距离存在后逐条打印；余弦距离越小越相似。
        if documents is not None and distances is not None:
            for i in range(len(result["ids"][0])):
                print(
                    f"ids: {result['ids'][0][i]}, "
                    f"内容: {documents[0][i][:30]}, "
                    f"距离: {distances[0][i]:.2f}"
                )
