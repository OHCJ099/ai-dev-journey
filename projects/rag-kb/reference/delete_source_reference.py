# projects/rag-kb/reference/delete_source_reference.py
# W13 第 4 日 第 1 件参考实现 —— 卡住 25 分钟以上再看。看完请关掉，自己重写一遍。
#
# 需求：delete_source(collection, source) -> int
#   删除某来源的全部块，返回删除条数；其他来源不受影响；来源不存在返回 0。
#
# 新接口 delete 的实跑输出（子教练取证）：
#   delete(where={"source": "A.md"})  → {'deleted': 2}   count 3 → 1
#   delete(where={"source": "不存在"}) → {'deleted': 0}   不报错
#   delete()                          → ValueError: At least one of ids,
#                                       where, or where_document must be provided


def delete_source(collection, source: str) -> int:
    """删掉某来源的全部块，返回删掉的条数。

    其他来源不受影响；来源不存在时返回 0（不报错）。
    """
    result = collection.delete(where={"source": source})
    return result["deleted"]
