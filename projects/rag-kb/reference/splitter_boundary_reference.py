# projects/rag-kb/reference/splitter_boundary_reference.py
# W9 挂账参考实现（按边界切分）—— 卡住 25 分钟以上再看。看完关掉，自己重写。
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


# splitter.py 里的老函数（硬切回退用），复制一份让本文件能单独运行。
def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """固定字数切分（老逻辑）"""
    if chunk_size - overlap <= 0:
        raise ValueError("chunk_size - overlap 必须大于 0")
    if overlap < 0:
        raise ValueError("overlap 必须大于等于 0")
    chunks = []
    for start in range(0, len(text), chunk_size - overlap):
        chunks.append(text[start : start + chunk_size])
    return chunks


def _pack(units: list[str], sep: str, chunk_size: int) -> list[str]:
    """贪心装箱：单位依次入块，装不下就封口。sep 是连接符（段落 '\n\n'、句子 ''）。"""
    chunks: list[str] = []
    current = ""
    for unit in units:
        if not unit:
            continue
        if not current:
            current = unit
        elif len(current) + len(sep) + len(unit) <= chunk_size:
            current += sep + unit
        else:
            chunks.append(current)
            current = unit
    if current:
        chunks.append(current)
    return chunks


def split_by_boundary(text: str, chunk_size: int) -> list[str]:
    """按边界切分 v1：段落优先 → 超长段拆句 → 超长句硬切；不重叠。"""
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")
    if not text:
        return []

    chunks: list[str] = []
    current = ""
    for para in text.split("\n\n"):
        if not para:
            continue
        if len(para) <= chunk_size:
            # 正常段落：试着装进当前块（空行也算长度），装不下就封口。
            if not current:
                current = para
            elif len(current) + 2 + len(para) <= chunk_size:
                current += "\n\n" + para
            else:
                chunks.append(current)
                current = para
        else:
            # 超长段：先封掉手头的块，再拆句装箱（句子之间不加空行）。
            if current:
                chunks.append(current)
                current = ""
            units: list[str] = []
            for sent in re.findall(r"[^。！？]+[。！？]?", para):
                if len(sent) > chunk_size:
                    units.extend(split_text(sent, chunk_size, 0))
                else:
                    units.append(sent)
            chunks.extend(_pack(units, "", chunk_size))
    if current:
        chunks.append(current)
    return chunks


if __name__ == "__main__":
    sample = (
        "第一段是普通段落，直接装块。"
        "\n\n"
        "第二段比较长，会被拆成句子再装箱。看看块边界是不是都落在句号后面。"
        "再加一两句凑够长度，让拆句这一步真的发生。再补一句确保超过六十个字。"
        "\n\n"
        "第三段里有一个超长句子它中间没有任何句末标点所以只能硬切"
        "它中间没有任何句末标点所以只能硬切它中间没有任何句末标点所以只能硬切。"
    )
    chunks = split_by_boundary(sample, 60)
    print(f"样例：chunk_size=60 → {len(chunks)} 块")
    for i, c in enumerate(chunks, start=1):
        print(f"[{i}] len={len(c)} 头: {c[:20]}… 尾: {c[-8:]}")
    print("空串:", split_by_boundary("", 500))
