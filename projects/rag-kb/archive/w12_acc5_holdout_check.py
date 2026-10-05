"""留出集机制复核（BuddyHub 通道）：5 道计分题跑 rerank，核对关键句是否在 top-3。

背景：原始留出集输出 w12_holdout_output.txt 已被 scratch 24h 清理删除；
DeepSeek 直连余额不足（402）。本脚本用 BuddyHub 本地反代独立复跑，
作「重排机制在留出集上有效」的交叉证据（模型与原始运行不同，非同一口径）。
"""

import sys
from pathlib import Path

sys.path.insert(0, r"D:/dev/ai-dev-journey/projects/rag-kb")

import rerank as R
from dotenv import dotenv_values
from loader import load_documents
from openai import OpenAI
from qa import build_index

vals = dotenv_values(Path(r"D:/Hermes/.env"))
key = vals.get("WORKBUDDY_API_KEY")
assert key, "没读到 WORKBUDDY_API_KEY"

R.client = OpenAI(base_url="http://127.0.0.1:8787/v1", api_key=key, timeout=180.0)
R.MODEL = "deepseek-v4.1-flash-ai-think-max"

docs = load_documents(Path(r"D:/dev/ai-dev-journey/projects/rag-kb/data"))
collection = build_index(docs)
print(f"[建库] {len(docs)} 份文档")

CASES = [
    ("Q13", "公司的借款审批流程是什么？", ["借款", "审批"]),
    ("Q14", "参加统一安排食宿的会议，还能领伙食补助吗？", ["伙食补助"]),
    ("Q15", "重点部位消防演练频次是多久一次？", ["每半年"]),
    ("Q19", "加班后调休具体要怎么安排？", ["补休", "调休"]),
    (
        "Q20",
        "因工作需要没休完年假，公司会支付报酬吗？这笔报酬是否包含绩效奖金？",
        ["年休假工资报酬", "报酬"],
    ),
]

for tag, q, phrases in CASES:
    print(f"\n===== {tag}：{q} =====")
    try:
        out = R.rerank(collection, q, recall_k=10, k=3)
    except Exception as e:  # noqa: BLE001 —— 探针逐题容错：任何 API 失败都继续下一题
        print(f"[ERROR] {type(e).__name__}: {e}")
        continue
    text = "\n".join(t for _, _, t in out)
    for n, src, txt in out:
        print(f"{n}. {src} | {txt[:70]!r}")
    hits = [p for p in phrases if p in text]
    print(f"关键短语 {phrases} → 命中 {hits}")
