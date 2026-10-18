chunks = [
    ("文件名A", "正文"),
    ("文件名B", "正文"),
    ("文件名A", "正文"),
    ("文件名B", "正文"),
]


def build_ids(chunks):
    counter = {}
    ids = []

    if chunks == []:
        return []

    for chunk in chunks:
        source = chunk[0]
        counter[source] = counter.get(source, 0) + 1
        ids.append(f"{source}-{counter[source]}")
    return ids


print(build_ids(chunks))
print(build_ids(chunks))
