"""w12_acc5_splitter_probe2.py — 加练①「边界切分」破坏性探针（口径修正版）。

修正：原「内容保留」检查用了 str.split() 口径（对空白敏感）→ 块边界不保留段落空行
是设计行为，导致误报 FAIL。改为「去空白后逐字符比对」（检查有无丢字）。
"""

import re
import sys

sys.path.insert(0, r"D:/dev/ai-dev-journey/projects/rag-kb")
from splitter import docs, split_by_boundary, split_text

results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond), str(extra)))


def nows(s):
    return re.sub(r"\s+", "", s)


# 1) 空串 / 纯空白
check("空串 -> []", split_by_boundary("", 500) == [])
check("纯空白 -> []", split_by_boundary("  \n\n   ", 500) == [])

# 2) 非法参数
for bad in (0, -1):
    try:
        split_by_boundary("abc", bad)
        check(f"chunk_size={bad} -> ValueError", False, "没报错")
    except ValueError:
        check(f"chunk_size={bad} -> ValueError", True)

# 3) 旧 split_text 守卫回归（09-29 已验收行为不许破坏）
for cs, ov in ((0, 0), (5, 5), (5, -1)):
    try:
        split_text("abc", cs, ov)
        check(f"split_text({cs},{ov}) -> ValueError", False, "没报错")
    except ValueError:
        check(f"split_text({cs},{ov}) -> ValueError", True)

# 4) 无标点超长文本硬切：每块 <= 上限、无丢字
t = "无标点" * 300
c = split_by_boundary(t, 60)
check("无标点硬切：每块<=60", all(len(x) <= 60 for x in c), f"{len(c)} 块")
check("无标点硬切：无丢字", nows("".join(c)) == nows(t))

# 5) chunk_size=1
check("cs=1：逐字切", split_by_boundary("abc", 1) == ["a", "b", "c"])

# 6) 连续空行 + 首尾空行
c5 = split_by_boundary("第一段。\n\n\n\n第二段。", 500)
check(
    "多空行：1 块含两段", len(c5) == 1 and "第一段。" in c5[0] and "第二段。" in c5[0]
)
check("首尾空行 -> 1 块", split_by_boundary("\n\n甲。\n\n", 500) == ["甲。"])
check("段落恰好=上限", split_by_boundary("甲" * 60, 60) == ["甲" * 60])

# 7) 5 文档 x {300,500}：上限 / 坏接缝 / 空块 / 无丢字（去空白口径）
for cs in (300, 500):
    bad_total = 0
    for d in docs:
        chunks = split_by_boundary(d["text"], cs)
        over = [len(x) for x in chunks if len(x) > cs]
        blanks = [i for i, x in enumerate(chunks) if not x.strip()]
        bad = 0
        for i in range(len(chunks) - 1):
            a, b = chunks[i], chunks[i + 1]
            if not (a[-1] in "。！？：" or (a[-15:] + "\n\n" + b[:15]) in d["text"]):
                bad += 1
        bad_total += bad
        keep = nows("".join(chunks)) == nows(d["text"])
        check(
            f"cs={cs} {d['source']} 上限/空块/无丢字",
            not over and not blanks and keep,
            f"over={len(over)} blank={len(blanks)} keep={keep} n={len(chunks)}",
        )
    if cs == 500:
        check("cs=500 坏接缝=0（对拍口径）", bad_total == 0, f"bad={bad_total}")
    else:
        check("cs=300 坏接缝（信息项）", True, f"bad={bad_total}")

# 8) 超大 chunk_size
big = split_by_boundary(docs[0]["text"], 10**9)
check("超大 cs：不炸", len(big) >= 1, f"{len(big)} 块")

fails = [r for r in results if not r[1]]
for name, ok, extra in results:
    print(("PASS " if ok else "FAIL ") + name + (f" | {extra}" if extra else ""))
print("=" * 40)
print(f"total={len(results)} pass={len(results) - len(fails)} fail={len(fails)}")
