# projects/rag-kb/reference/loader_reference.py
# W9 第 1 件参考实现 —— 卡住 25 分钟以上再看。看完请关掉，自己重写一遍。
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def clean_text(text: str) -> str:
    """清洗：统一换行 / 去每行首尾空白 / 连续空行压缩"""
    # ① 统一换行
    text = text.replace("\r\n", "\n")
    # ② 拆行
    lines = text.split("\n")
    # ③ 每行去首尾空白
    lines = [line.strip() for line in lines]
    # ④ 缝回去
    text = "\n".join(lines)
    # ⑤ 连续空行压缩到最多一个空行
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    # ⑥ 整段首尾也清掉
    return text.strip()


def load_documents(data_dir: Path) -> list[dict[str, str]]:
    """读 data_dir 下所有 .md / .txt，返回 [{"source": 文件名, "text": 清洗后全文}, ...]"""
    files = sorted(data_dir.glob("*.md")) + sorted(data_dir.glob("*.txt"))
    docs = []
    for path in files:
        raw = path.read_text(encoding="utf-8")
        docs.append({"source": path.name, "text": clean_text(raw)})
    return docs


if __name__ == "__main__":
    # 1) 对比表：清洗前 → 清洗后 字符数
    for path in sorted(DATA_DIR.glob("*.md")) + sorted(DATA_DIR.glob("*.txt")):
        raw = path.read_text(encoding="utf-8")
        cleaned = clean_text(raw)
        print(f"{path.name}: 清洗前 {len(raw)} → 清洗后 {len(cleaned)}")

    # 2) 脏样本测试（repr 看不可见字符）
    dirty = "  第一行  \r\n\r\n\r\n\t第二行\n\n\n\n第三行   "
    print("dirty repr:", repr(dirty))
    print("clean repr:", repr(clean_text(dirty)))
    print("空串:", repr(clean_text("")))
    print("纯空格:", repr(clean_text("   ")))

    # 3) load_documents
    docs = load_documents(DATA_DIR)
    print(f"共 {len(docs)} 份")
    for d in docs:
        print(f"  {d['source']}: {len(d['text'])} 字符")
