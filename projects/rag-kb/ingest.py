from pathlib import Path

from index_store import add_chunks, delete_source, open_index
from loader import load_document
from retriever import embed
from splitter import split_text

CHUNK_SIZE = 500
OVERLAP = 50


def ingest_file(path: str | Path, index_path: str | Path, replace: bool = False) -> int:
    file = load_document(path)
    chunks = split_text(file["text"], CHUNK_SIZE, OVERLAP)
    if len(chunks) == 0:
        raise ValueError(f"文件{file['source']}: chunks块为0")

    embeddings = []
    for chunk in chunks:
        embeddings.append(embed(chunk))

    collection = open_index(index_path)

    # ★ 覆盖逻辑加在这里。想清楚两件事：
    if replace:
        #   ① 删旧块用哪个函数？（你 10-09 自己写过，可以直接调）
        delete_source(collection, file["source"])
        #   ② 这一步放在「算向量」之前还是之后？为什么？
    #      （不要急着写，讲回第②题就问这个）
    add_count = add_chunks(collection, file["source"], chunks, embeddings)
    return add_count
