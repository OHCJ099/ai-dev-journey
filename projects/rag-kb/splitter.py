from pathlib import Path

from loader import load_documents

DATA_DIR = Path(__file__).parent / "data"

# 同目录的模块，直接 import 文件名（不带 .py）
docs = load_documents(DATA_DIR)  # 这样拿到的是清洗后的文本，正好串起整条流水线


def split_text(text, chunk_size, overlap) -> list[str]:
    chunk_list = []
    if chunk_size - overlap <= 0:
        raise ValueError("chunk_size - overlap 必须大于 0")
    if overlap < 0:
        raise ValueError("overlap 必须大于等于 0")
    for start in range(0, len(text), chunk_size - overlap):
        chunk_list.append(text[start : start + chunk_size])
    return chunk_list


if __name__ == "__main__":
    try:
        chunks = split_text(docs[2]["text"], 10, -5)
    except ValueError as e:
        print(f"{e}")
    else:
        for num, chunk in enumerate(chunks):
            print(f"第{num + 1}块 字数: {len(chunk)} 内容: {chunk[0:30]}")
