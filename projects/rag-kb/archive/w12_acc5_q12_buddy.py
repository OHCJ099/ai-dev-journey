"""Q12 复核 v3：BuddyHub 反代旁路（DeepSeek 402 时的备用通道），验证重排机制把工伤块提上来。

说明：10-04 的 Q12 翻盘证据（w12_optimB_output.txt）已被 scratch 24h 清理删除；
DeepSeek 直连现为 402（余额不足）。本脚本用 BuddyHub 本地反代独立复跑一次，
作为「重排机制有效」的交叉证据（注：模型不同，不能替代原始数字，只作机制验证）。
"""

import sys
from pathlib import Path

sys.path.insert(0, r"D:/dev/ai-dev-journey/projects/rag-kb")

import rerank as R
from dotenv import dotenv_values
from loader import load_documents
from openai import OpenAI
from qa import build_index

# BuddyHub 密钥从 Hermes 侧 .env 读取（只打印长度，不打印值）
vals = dotenv_values(Path(r"D:/Hermes/.env"))
key = vals.get("WORKBUDDY_API_KEY")
print("WORKBUDDY_API_KEY 长度:", len(key) if key else None)
assert key, "没读到 WORKBUDDY_API_KEY"

client = OpenAI(base_url="http://127.0.0.1:8787/v1", api_key=key, timeout=180.0)
R.client = client
R.MODEL = "deepseek-v4.1-flash-ai-think-max"

docs = load_documents(Path(r"D:/dev/ai-dev-journey/projects/rag-kb/data"))
collection = build_index(docs)
print(f"[建库] {len(docs)} 份文档")

out = R.rerank(collection, "工伤假能休几天？", recall_k=10, k=3)
print("\n=== rerank 输出（BuddyHub 通道）===")
for n, src, txt in out:
    flag = "  <<< 含「工伤」" if "工伤" in txt else ""
    print(f"{n}. {src} | {txt[:60]!r}{flag}")

first = out[0][2] if out else ""
print("\n第 1 条含「工伤」：", "工伤" in first)
print("（机制验证：工伤块能否被重排提到第 1 条）")
