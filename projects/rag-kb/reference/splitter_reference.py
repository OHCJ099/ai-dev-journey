# projects/rag-kb/reference/splitter_reference.py
# W9 第 2 件参考实现 —— 卡住 25 分钟以上再看。看完关掉，自己重写。
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """固定字数切分：每块 chunk_size 字符，相邻块重叠 overlap 字符"""
    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(text), step):
        chunks.append(text[start : start + chunk_size])
    return chunks


if __name__ == "__main__":
    # 参考直接读原文；你自己的 splitter.py 在上一级目录，可以 from loader import load_documents 拿清洗后的
    text = (DATA_DIR / "考勤制度.md").read_text(encoding="utf-8")

    for size in (200, 500):
        chunks = split_text(text, size, 50)
        print(f"=== chunk_size={size}, overlap=50 → {len(chunks)} 块 ===")
        for i, c in enumerate(chunks, start=1):
            print(f"[{i}] {c[:30]} … 共 {len(c)} 字符")
        print()
