# projects/rag-kb/run_experiments.py
"""W9 切分对比实验 —— 跑一遍，输出直接喂 experiments.md"""

from pathlib import Path

from loader import load_documents
from splitter import split_text

DATA_DIR = Path(__file__).parent / "data"
DOC_NAME = "报销制度.md"

docs = load_documents(DATA_DIR)
text = ""
for d in docs:
    if d["source"] == DOC_NAME:
        text = d["text"]

print(f"文档: {DOC_NAME} | 清洗后 {len(text)} 字符")
print()

print("== 实验 1: chunk_size 对比（overlap=50）==")
for size in (200, 500, 1000):
    chunks = split_text(text, size, 50)
    avg = sum(len(c) for c in chunks) / len(chunks)
    print(
        f"chunk_size={size}: 块数={len(chunks)} 平均长度={avg:.0f} 末块={len(chunks[-1])}"
    )
print()

print("== 实验 2: overlap 对比（chunk_size=500）==")
for ov in (0, 50, 100):
    chunks = split_text(text, 500, ov)
    print(f"overlap={ov}: 块数={len(chunks)}")
    for num, c in enumerate(chunks, start=1):
        print(f"  [{num}] 头:{c[:20]} 尾:{c[-20:]}")
