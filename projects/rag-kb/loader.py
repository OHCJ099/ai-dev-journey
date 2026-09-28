# projects/rag-kb/loader.py
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"   # 锚定，不管从哪个目录跑都对


def clean_text(text: str) -> str:
    """清洗：统一换行 / 去每行首尾空白 / 连续空行压缩"""
    # ① 把 "\r\n" 全部换成 "\n"
    text_replace = text.replace("\r\n","\n")
    # ② 用 "\n" 拆成 lines
    lines = text_replace.split("\n")
    # ③ 每行 strip()（用卡片 6 的写法，或用 for 循环）
    lines_strip = [line.strip() for line in lines]
    # ④ 用 "\n" 把 lines 缝回去（卡片 4）
    lines_join = ("\n".join(lines_strip))
    # ⑤ 连续空行压缩到最多一个空行
    while "\n\n\n" in lines_join:          # 只要还查得到，就继续
        lines_join = lines_join.replace("\n\n\n", "\n\n")
    return lines_join.strip()              # 循环外收尾



def load_documents(data_dir: Path) -> list[dict[str, str]]:
    docs = []
    """读 data_dir 下所有 .md / .txt，返回 [{"source": 文件名, "text": 清洗后全文}, ...]"""
    # 卡片 1、2 的 glob + sorted
    files = sorted(data_dir.glob("*.md"))
    for path in files:
        # 每份：read_text(encoding="utf-8") → clean_text → 装进 dict → append
        raw = path.read_text(encoding="utf-8")
        text = clean_text(raw)
        doc = {"source": path.name, "text": text}
        docs.append(doc)
    return(docs)


if __name__ == "__main__":
    data_dir = Path(__file__).parent / "data"
    dirty_docs = []
    dirty_files = sorted(data_dir.glob("*.md"))
    for path in dirty_files:
        raw = path.read_text(encoding="utf-8")
        doc = {"source": path.name, "text": raw}
        dirty_docs.append(doc)

    print("清洗前的字数：")
    for num in dirty_docs:
        number = len(num["text"])
        print(f"{num['source']}: {number}字")

    print("清洗后的字数：")
    clean = load_documents(DATA_DIR)
    for num in clean:
        number = len(num["text"])
        print(f"{num['source']}: {number}字")

    # 2) 脏样本测试（用 repr 打印，见卡片 7）：
    dirty = "  第一行  \r\n\r\n\r\n\t第二行\n\n\n\n第三行"

    cleaned = clean_text(dirty)
    print(cleaned)
    #    再加两个边界：clean_text("") 和 clean_text("   ") 分别返回什么？
    # 3) docs = load_documents(DATA_DIR)：打印共几份 + 每份 source 和字符数
    print("dirty repr:", repr(dirty))
    print("clean repr:", repr(clean_text(dirty)))
    print("空串:", repr(clean_text("")))
    print("纯空格:", repr(clean_text("   ")))