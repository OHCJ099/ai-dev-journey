import math
import os
from pathlib import Path

from dotenv import load_dotenv
from loader import load_documents
from openai import OpenAI
from splitter import split_text

load_dotenv()

key = os.getenv("DASHSCOPE_API_KEY")
if not key:
    raise SystemExit("没找到 DASHSCOPE_API_KEY，请检查 .env")


def embed(text: str) -> list[float]:
    client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=key,
    )
    resp = client.embeddings.create(model="text-embedding-v4", input=text)
    vec = resp.data[0].embedding
    return vec


def cos_sim(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


def retrieve(
    question: str, chunks: list[str], k: int = 3, min_score: float | None = None
) -> list[tuple[str, float]]:

    question_embed = embed(question)
    embed_chunks_list = []
    finally_cossin = []
    before_sorte = []

    for chunk in chunks:
        embed_chunks_list.append(embed(chunk))

    for chunk in embed_chunks_list:
        Vec_value = cos_sim(question_embed, chunk)
        finally_cossin.append(Vec_value)

    for y in zip(chunks, finally_cossin):
        before_sorte.append((y[0], y[1]))

    after_sorted = sorted(before_sorte, key=lambda w: w[1], reverse=True)

    if min_score is None:
        return after_sorted[:k]
    else:
        filted = [i for i in after_sorted if i[1] >= min_score]
        return filted[:k]


if __name__ == "__main__":
    docs = load_documents(Path(__file__).parent / "data")
    chunks = []
    for doc in docs:
        chunks.extend(split_text(doc["text"], 500, 50))

    question_list = [
        "员工请假的规则是什么？",
    ]

    for question in question_list:
        anwsers = retrieve(question, chunks, 10)
        for anwser in anwsers:
            print(f"回复: {anwser[0][:100]} 相似值: {anwser[1]:.2f}")
