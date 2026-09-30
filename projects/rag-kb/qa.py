# projects/rag-kb/qa.py
"""W11 第 1 件：拼上下文 + 生成回答（RAG 的最后一公里）。

跑法（仓库根目录）：uv run python projects/rag-kb/qa.py
"""

import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from loader import load_documents
from openai import OpenAI
from retriever import embed  # 复用 W10 的向量化函数
from splitter import split_text

DATA_DIR = Path(__file__).parent / "data"
ENV_FILE = Path(__file__).parent.parent.parent / ".env"
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-flash"

load_dotenv(ENV_FILE)
ds_key = os.getenv("DEEPSEEK_API_KEY")
if not ds_key:
    raise SystemExit("没找到 DEEPSEEK_API_KEY，请检查 .env")

client = OpenAI(base_url=BASE_URL, api_key=ds_key, timeout=60.0)


def build_index(docs):
    # 创建chroma连接
    client = chromadb.Client()
    collection = client.create_collection(
        name="zhidu",
        metadata={"hnsw:space": "cosine"},
    )

    # 库的对应列表 b_ids字符串编号, b_embed对应向量, b_metadatas文件名
    b_ids = []
    b_embed = []
    b_metadatas = []

    # 切片块列表
    chunks = []

    for doc in docs:
        for chunk in split_text(doc["text"], 500, 50):
            chunks.append(chunk)
            b_metadatas.append({"source": doc["source"]})

    for i in range(len(chunks)):
        b_ids.append(f"chunk_{i}")

    for chunk in chunks:
        b_embed.append(embed(chunk))

    collection.add(
        ids=b_ids,  # ★ 54 个不重复的字符串编号（提示：循环 + f-string）
        metadatas=b_metadatas,  # 文件名
        documents=chunks,  # ★ 块文本列表（就是 chunks）
        embeddings=b_embed,  # ★ 54 个向量：循环里每个块过一遍 embed()，append 进列表
    )

    return collection


def retrieve_hits(collection, question: str, k: int = 3) -> list[tuple[int, str, str]]:
    question_embed = embed(question)

    result = collection.query(
        query_embeddings=[question_embed],
        n_results=k,
    )

    hits = []

    documents = result["documents"]
    metadata = result["metadatas"]

    if documents is not None and metadata is not None:
        for num, (file_info, chunk) in enumerate(
            zip(metadata[0], documents[0]), start=1
        ):
            hits.append((num, file_info["source"], chunk))

    return hits


def build_context(hits: list[tuple[int, str, str]]) -> str:
    parts = []

    for num, resource, chunk in hits:
        parts.append(f"[{num}] 来源：{resource}\n{chunk}")

    return "\n\n".join(parts)


def ask(collection, question: str, k: int = 3) -> str:
    """检索 → 拼上下文 → 调 DeepSeek 生成回答（非流式、关思考模式），返回回答文本。

    消息结构：system 放角色 + 规则；user 放 材料 + 问题。
    """
    # <你的实现>
    hits = retrieve_hits(collection, question, k)
    context = build_context(hits)

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "你是实用的实用的AI助手，用中文回答",
            },
            {"role": "user", "content": f"参考材料：\n{context}\n\n问题：{question}"},
        ],
        extra_body={"thinking": {"type": "disabled"}},  # 关掉思考模式，省 token
    )

    reply = resp.choices[0].message.content
    if not reply:
        return "模型没有返回回答。"
    return reply


if __name__ == "__main__":
    docs = load_documents(DATA_DIR)
    collection = build_index(docs)

    questions = [
        "请假需要提前多久申请？",
        "擅自离岗的话会怎么样",
    ]
    for question in questions:
        print(f"== {question} ==")
        print(ask(collection, question))

    # data = collection.get(include=["metadatas"])
    # print(data["metadatas"])
