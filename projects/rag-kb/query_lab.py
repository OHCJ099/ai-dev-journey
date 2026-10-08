from index_store import open_index
from retriever import embed


def query_index(collection, question, k=3, source=None):
    if not question or not str(question).strip():
        raise ValueError(f"问题[{question!r}]为空")

    q = str(question).strip()
    q_embed = embed(q)

    where = {"source": source} if source else None
    result = collection.query(
        query_embeddings=[q_embed],
        n_results=min(k, collection.count()),
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    docs = result["documents"][0]
    metas = result["metadatas"][0]
    return [(m.get("source"), d) for m, d in zip(metas, docs)]


if __name__ == "__main__":
    collection = open_index("D:/Hermes/cache/scratch/w13/ingest_lab")
    q = "员工请假需要提前多久申请？"

    print("① 正常问题")
    for i, (src, doc) in enumerate(query_index(collection, q), 1):
        print(f"  {i}. 来源={src} | {doc[:30]}")

    for label, bad in [("② 空串", ""), ("③ 纯空格", "   ")]:
        print(label)
        try:
            query_index(collection, bad)
        except ValueError as v:
            print(f"  {v}")

    print("④ 不存在的来源")
    name = "不存在.md"
    res = query_index(collection, q, source=name)
    if not res:
        print(f"  没找到来源为 {name} 的内容")
    else:
        print(f"  返回 {len(res)} 条")

    print("⑤ k=100")
    print(f"  返回 {len(query_index(collection, q, k=100))} 条")
