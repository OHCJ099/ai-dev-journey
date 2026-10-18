def build_ids(docs: list[dict]) -> list[str]:
    if not docs:
        return []

    count_list = []
    counter = {}  # 记录每个 source 已出现的次数

    for doc in docs:
        source = doc["source"]
        counter[source] = counter.get(source, 0) + 1
        count_list.append({"source": source, "id": counter[source]})

    ids = [f"{i['source']}-{i['id']}" for i in count_list]
    return ids


docs = [
    {"source": "<文件名A>", "text": "<正文>"},
    {"source": "<文件名A>", "text": "<正文>"},
    {"source": "<文件名B>", "text": "<正文>"},
]

print(build_ids(docs))

assert build_ids(
    [
        {"source": "A", "text": "x"},
        {"source": "B", "text": "y"},
        {"source": "A", "text": "z"},
    ]
) == ["A-1", "B-1", "A-2"]
assert build_ids([]) == []
