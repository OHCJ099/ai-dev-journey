# 文本切分：将长文分成小块，相邻块可保留重叠内容。
from pathlib import Path

from loader import load_documents

DATA_DIR = Path(__file__).parent / "data"

# 此处在导入模块时也会加载文档，供下方演示使用。
docs = load_documents(DATA_DIR)  # 这样拿到的是清洗后的文本，正好串起整条流水线


# chunk_size 是每块字符数，overlap 是相邻块重叠的字符数。
def split_text(text, chunk_size, overlap) -> list[str]:
    chunk_list = []
    # 每次前进的字符数必须大于 0，重叠长度也不能为负。
    if chunk_size - overlap <= 0:
        raise ValueError("chunk_size - overlap 必须大于 0")
    if overlap < 0:
        raise ValueError("overlap 必须大于等于 0")
    # 每次前进 chunk_size - overlap 个字符，再截取一块文本。
    for start in range(0, len(text), chunk_size - overlap):
        # 切片超出文本末尾时会自动截断，因此最后一块可能较短。
        chunk_list.append(text[start : start + chunk_size])
    return chunk_list


# 直接运行时演示参数检查：负数 overlap 会触发 ValueError。
if __name__ == "__main__":
    try:
        chunks = split_text(docs[2]["text"], 10, -5)
    except ValueError as e:
        print(f"{e}")
    # try 没有抛出异常时，才逐块打印切分结果。
    else:
        for num, chunk in enumerate(chunks):
            print(f"第{num + 1}块 字数: {len(chunk)} 内容: {chunk[0:30]}")
