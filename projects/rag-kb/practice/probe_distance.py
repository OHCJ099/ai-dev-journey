# projects/rag-kb/practice/probe_distance.py
"""阈值标定探针：只读正式索引，打印三档问题最近 3 条的距离。

用途 —— 换语料 / 换 embedding 模型 / 换块大小之后，重新标定 config.MAX_DISTANCE。
判据：相关档的**上限**与无关档的**下限**之间必须留出一道缝，阈值只能落在这道缝里。

跑法（仓库根目录）：uv run python projects/rag-kb/practice/probe_distance.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from index_store import open_index
from retriever import embed

collection = open_index(config.INDEX_PATH)
print("块数:", collection.count())

groups = {
    "相关（库里有答案）": ["病假需要什么证明", "出差住宿标准是多少"],
    "半相关（主题在、答案不在）": ["加班有加班费吗"],
    "无关（主题完全不在）": ["公积金怎么提取", "年终奖怎么发", "公司有食堂补贴吗"],
}

for label, questions in groups.items():
    for q in questions:
        result = collection.query(
            query_embeddings=[embed(q)],
            n_results=3,
            include=["documents", "metadatas", "distances"],
        )
        metas = result["metadatas"] or [[]]
        docs = result["documents"] or [[]]
        dists = result["distances"] or [[]]
        print(f"== {label} | {q} ==")
        for meta, doc, dist in zip(metas[0], docs[0], dists[0]):
            print(f"  {dist:.4f}  {(meta or {}).get('source')}  {doc[:30]}")
