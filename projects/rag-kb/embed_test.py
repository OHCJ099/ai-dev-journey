import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 读仓库根目录的 .env —— 本脚本要在仓库根目录运行

key = os.getenv("DASHSCOPE_API_KEY")
if not key:
    raise SystemExit("没找到 DASHSCOPE_API_KEY，请检查 .env")

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=key,
)
resp = client.embeddings.create(model="text-embedding-v4", input="怎么报销差旅费")
vec = resp.data[0].embedding
print(f"向量维度: {len(vec)}")
print(f"前 5 个数: {vec[:5]}")
