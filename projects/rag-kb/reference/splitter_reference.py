# projects/rag-kb/reference/splitter_reference.py
# W9 第 2 件参考实现 —— 卡住 25 分钟以上再看。看完关掉，自己重写。
from pathlib import Path

# 当前文件在 reference 中，制度文档位于上一级的 data 目录。
DATA_DIR = Path(__file__).parent.parent / "data"


# 这个参考版本未检查参数，调用时需保证 0 <= overlap < chunk_size。
def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """固定字数切分：每块 chunk_size 字符，相邻块重叠 overlap 字符"""
    chunks = []
    # 步长小于块大小时，相邻块就会保留重复的内容。
    step = chunk_size - overlap
    # 从每个起点截取一块；最后一块不足指定长度时自动截断。
    for start in range(0, len(text), step):
        chunks.append(text[start : start + chunk_size])
    return chunks


if __name__ == "__main__":
    # 演示直接读取原文，不经过 loader 的清洗。
    text = (DATA_DIR / "考勤制度.md").read_text(encoding="utf-8")

    # 固定重叠 50 字符，比较两种块大小的切分结果。
    for size in (200, 500):
        chunks = split_text(text, size, 50)
        print(f"=== chunk_size={size}, overlap=50 → {len(chunks)} 块 ===")
        # 从 1 编号，只显示每块前 30 个字符和总长度。
        for i, c in enumerate(chunks, start=1):
            print(f"[{i}] {c[:30]} … 共 {len(c)} 字符")
        print()
