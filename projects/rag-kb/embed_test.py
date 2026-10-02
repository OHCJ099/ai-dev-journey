# 最小向量化示例：把一句话转换成表示语义的数字列表。
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 读仓库根目录的 .env —— 本脚本要在仓库根目录运行

# 从环境变量读取密钥，缺少时停止执行。
key = os.getenv("DASHSCOPE_API_KEY")
if not key:
    raise SystemExit("没找到 DASHSCOPE_API_KEY，请检查 .env")

# 通过兼容 OpenAI 的接口连接 DashScope 向量服务。
client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=key,
)
# 请求文本向量；第一条结果对应本次传入的句子。
resp = client.embeddings.create(model="text-embedding-v4", input="怎么报销差旅费")
vec = resp.data[0].embedding
# 向量维度就是数字个数，这里只打印前 5 个数供观察。
print(f"向量维度: {len(vec)}")
print(f"前 5 个数: {vec[:5]}")
