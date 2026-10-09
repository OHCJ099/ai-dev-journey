# projects/rag-kb/id_practice3.py
# W13 第 4 日 第 0 件：每个来源各自的块数


def count_by_source(chunks: list[tuple[str, str]]) -> dict[str, int]:
    # ① 容器放哪？想清楚再写这一行
    count_list = {}
    # ② 遍历 chunks，每个元组解包成 (source, _text)
    for source, _chunk in chunks:
        # ③ 这个来源的计数 +1（提示：counts.get(source, 0) + 1）
        count_list[source] = count_list.get(source, 0) + 1
    return count_list


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
