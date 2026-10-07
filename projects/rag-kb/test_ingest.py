import shutil
import sys
from pathlib import Path

from index_store import open_index
from ingest import ingest_file
from loader import load_document
from splitter import split_text

# 练习库放在 scratch 专用子目录，不写正式语料、不写生产索引。
INDEX_PATH = Path("D:/Hermes/cache/scratch/w13/ingest_lab")

FAKE_VECTORS = [[0.1, 0.2, 0.3], [0.9, 0.8, 0.7]]

FILE_PATH = Path(__file__).parent / "data" / "考勤制度.md"


def do_write():
    shutil.rmtree(INDEX_PATH, ignore_errors=True)
    doc = load_document(FILE_PATH)
    chunks = split_text(doc["text"], 500, 50)
    print(chunks)
    print(f"预计计算向量[{len(chunks)}]次")

    write_times = ingest_file(FILE_PATH, INDEX_PATH)
    print(f"实际写入了[{write_times}]次")


def do_read():
    source = FILE_PATH.name
    collection = open_index(INDEX_PATH)

    print("重开进程 count:", collection.count())
    data = collection.get(where={"source": source})

    print("ids:", data["ids"])
    print("documents:", data["documents"])
    print("metadatas:", data["metadatas"])


def do_check():
    collection = open_index(INDEX_PATH)
    before = collection.count()
    try:
        ingest_file(FILE_PATH, INDEX_PATH)  # 同一文件再写一次
        print("没抛错（该拦的没拦住）")
    except ValueError as e:
        print(f"改前 {before} | 改后 {collection.count()} | ValueError: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in {"write", "read", "check"}:
        print("用法：uv run python projects/rag-kb/test_ingest.py <write|read>")
        raise SystemExit(1)
    if sys.argv[1] == "write":
        do_write()
    elif sys.argv[1] == "read":
        do_read()
    else:
        do_check()
