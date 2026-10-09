# projects/rag-kb/reference/id_practice3_reference.py
# W13 第 4 日 第 0 件参考实现 —— 卡住 25 分钟以上再看。看完请关掉，自己重写一遍。
#
# 需求：count_by_source(chunks) -> dict[str, int]
#   输入 [(<文件名>, <正文>), ...]，返回每个来源各自的块数。
#   硬性要求：连续调用两次，结果必须完全相同（不得跨调用累积）。
#
# 实跑输出：
#   第 1 次: {'A.md': 3, 'B.md': 2}
#   第 2 次: {'A.md': 3, 'B.md': 2}
#   两次相同: True
#   空列表: {}


def count_by_source(chunks: list[tuple[str, str]]) -> dict[str, int]:
    # 容器写在函数体里 —— 每次调用都是新的，不会跨调用累积。
    counts: dict[str, int] = {}
    for source, _text in chunks:
        # .get(key, 0) = 拿不到就当作 0，再 +1 存回去。
        counts[source] = counts.get(source, 0) + 1
    return counts


if __name__ == "__main__":
    data = [
        ("A.md", "a1"),
        ("B.md", "b1"),
        ("A.md", "a2"),
        ("B.md", "b2"),
        ("A.md", "a3"),
    ]
    print("第 1 次:", count_by_source(data))
    print("第 2 次:", count_by_source(data))
    print("两次相同:", count_by_source(data) == count_by_source(data))
    print("空列表:", count_by_source([]))
