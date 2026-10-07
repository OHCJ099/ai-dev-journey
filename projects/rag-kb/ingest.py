from pathlib import Path

from index_store import add_chunks, open_index
from loader import load_document
from retriever import embed
from splitter import split_text

CHUNK_SIZE = 500
OVERLAP = 50


def ingest_file(path: str | Path, index_path: str | Path) -> int:
    """一个文件 → 切块 → 逐块向量化 → 写进索引。返回写入的块数。"""
    # ① 加载
    file = load_document(path)
    # ② 切块
    chunks = split_text(file["text"], CHUNK_SIZE, OVERLAP)
    # ③ 逐块向量化（远程付费调用 —— 先报量）
    embeddings = []
    for chunk in chunks:
        embeddings.append(embed(chunk))
    # ④ 打开索引 + 入库
    collection = open_index(index_path)
    add_count = add_chunks(collection, file["source"], chunks, embeddings)
    return add_count
