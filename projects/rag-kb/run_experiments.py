# projects/rag-kb/run_experiments.py
"""W9 切分对比实验 —— 跑一遍，输出直接喂 experiments.md"""

from pathlib import Path

from loader import load_documents
from splitter import split_text

# 固定使用报销制度，让不同切分参数的结果可以直接比较。
DATA_DIR = Path(__file__).parent / "data"
DOC_NAME = "报销制度.md"

docs = load_documents(DATA_DIR)
text = ""
# 从已加载的文档中找到实验目标，取出清洗后的正文。
for d in docs:
    if d["source"] == DOC_NAME:
        text = d["text"]

print(f"文档: {DOC_NAME} | 清洗后 {len(text)} 字符")
print()

print("== 实验 1: chunk_size 对比（overlap=50）==")
# 固定重叠长度，只改变每块大小，比较块数和长度。
for size in (200, 500, 1000):
    chunks = split_text(text, size, 50)
    # 所有块的字符数相加，再除以块数，得到平均长度。
    avg = sum(len(c) for c in chunks) / len(chunks)
    print(
        f"chunk_size={size}: 块数={len(chunks)} 平均长度={avg:.0f} 末块={len(chunks[-1])}"
    )
print()

print("== 实验 2: overlap 对比（chunk_size=500）==")
# 固定每块大小，只改变重叠长度，观察相邻块如何衔接。
for ov in (0, 50, 100):
    chunks = split_text(text, 500, ov)
    print(f"overlap={ov}: 块数={len(chunks)}")
    # 编号从 1 开始，打印每块开头和结尾各 20 个字符。
    for num, c in enumerate(chunks, start=1):
        print(f"  [{num}] 头:{c[:20]} 尾:{c[-20:]}")
