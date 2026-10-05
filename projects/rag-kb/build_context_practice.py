hits = [
    (1, "文件A.md", "正文A"),
    (2, "文件B.md", "正文B"),
]


def build_context(hits):
    l = []
    for hit in hits:
        l.append(f"[{hit[0]}] 来源：{hit[1]}\n{hit[2]}")
    return "\n\n".join(l)


print(build_context(hits))


"""
    [<编号>] 来源：<文件名>
    <正文>
"""
