from pathlib import Path

import chromadb

# 调用方给一个目录，索引文件就落在它下面的这个子目录里。
INDEX_DIR_NAME = "chroma_index"

# collection 命名规则：3-512 个字符，只允许 [a-zA-Z0-9._-]，首尾必须是字母或数字。
COLLECTION_NAME = "zhidu_kb"


def open_index(path: str | Path):
    client = chromadb.PersistentClient(path=Path(path) / INDEX_DIR_NAME)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def add_chunks(
    collection, source: str, chunks: list[str], embeddings: list[list[float]]
) -> int:
    """把一批已经准备好的块写进 collection，返回写入的块数。

    契约（今天由你实现）：
    - 只处理一个来源 source；chunks 与 embeddings 必须逐位对应、长度相等；
    - chunks 里不许有空串或纯空白串；embeddings 不许为空；
    - 每块的 ID = 「source + "-" + 文内序号」，序号从 1 开始、只在本来源内计数
      （这样两份文档 ID 不会撞车，重复来源也能被你认出来）；
    - metadatas 每块一个 {"source": source}；
    - 同一个 source 重复写入 → 抛 ValueError，且库内容一个字符都不许变；
    - 校验要在真正写库之前全部做完 —— 写了一半再抛错，库就脏了。
    """
    existing = collection.get(where={"source": source}, include=[])
    # 判断传入值是否合法
    if len(embeddings) == 0:
        raise ValueError("向量批次为空")
    if len(chunks) != len(embeddings):
        raise ValueError("chunks 和 embeddings 数量不一致:")
    for chunk in chunks:
        if chunk.strip() == "":
            raise ValueError("此块为空，无效")
    if existing["ids"]:
        raise ValueError("目标ids已存在")
    else:
        ids = [f"{source}-{i + 1}" for i in range(len(chunks))]
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=[{"source": source} for _ in chunks],
        )

    return len(chunks)
