def blocks_per_source(chunks: list[tuple[str, str]]) -> list[tuple[str, int]]:
    counts = {}
    for chunk in chunks:
        counts[chunk[0]] = counts.get(chunk[0], 0) + 1
    return sorted(counts.items())


if __name__ == "__main__":
    chunks = [
        ("文件A", "正文"),
        ("文件D", "正文"),
        ("文件B", "正文"),
        ("文件C", "正文"),
        ("文件A", "正文"),
        ("文件B", "正文"),
    ]
    result = blocks_per_source(chunks)
    print(result)
