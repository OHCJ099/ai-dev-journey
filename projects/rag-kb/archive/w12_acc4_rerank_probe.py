"""10-04 验收：rerank 离线破坏性探针（monkeypatch client，零 API 调用）。

模仿 10-03 对 rewrite_query 的探针方法：替换 rerank.client 为假对象，
直接控制 LLM 回复内容，验证解析 / 兜底 / 去重 / 重编号全部分支。
"""

import sys

sys.path.insert(0, r"D:/dev/ai-dev-journey/projects/rag-kb")

import rerank as R


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResp:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, reply_holder):
        self.reply_holder = reply_holder

    def create(self, **kwargs):
        return FakeResp(self.reply_holder["reply"])


class FakeChat:
    def __init__(self, reply_holder):
        self.completions = FakeCompletions(reply_holder)


class FakeClient:
    def __init__(self, reply_holder):
        self.chat = FakeChat(reply_holder)


# 10 条假 hits（编号 1..10，来源 A/B，文本 T1..T10）
HITS = [(i, f"src{(i - 1) % 2}.md", f"T{i}") for i in range(1, 11)]


def run_case(name, reply, k=3, expect=None):
    holder = {"reply": reply}
    R.client = FakeClient(holder)
    R.retrieve_hits = lambda collection, question, k=10: HITS
    out = R.rerank(None, "假问题", recall_k=10, k=k)
    ok = expect is None or out == expect
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    print(f"    输入 reply={reply!r}")
    print(f"    输出={[(h[0], h[1], h[2]) for h in out]}")
    if not ok and expect is not None:
        print(f"    期望={[(h[0], h[1], h[2]) for h in expect]}")
    return ok


print("=== rerank 离线破坏性探针（10 组）===")
results = []

# 1 正常：取 3/1/7 → 输出应为 hits[2], hits[0], hits[6]，重编号 1/2/3
results.append(
    run_case(
        "1 正常 [3,1,7,2]",
        "[3,1,7,2]",
        expect=[(1, "src0.md", "T3"), (2, "src0.md", "T1"), (3, "src0.md", "T7")],
    )
)

# 2 content=None
results.append(run_case("2 content=None", None, expect=HITS[:3]))

# 3 非 JSON
results.append(run_case("3 非 JSON", "排序是 [1,2,3] 大概", expect=HITS[:3]))

# 4 非列表（dict）
results.append(run_case("4 非列表 dict", '{"order": [1,2,3]}', expect=HITS[:3]))

# 5 越界
results.append(run_case("5 越界 99", "[1,2,99]", expect=HITS[:3]))

# 6 含 0（下界）
results.append(run_case("6 含 0", "[0,1,2]", expect=HITS[:3]))

# 7 空列表
results.append(run_case("7 空列表", "[]", expect=HITS[:3]))

# 8 重复编号 [1,1,2,3] → 去重后 1,2,3
results.append(
    run_case(
        "8 重复编号",
        "[1,1,2,3]",
        expect=[(1, "src0.md", "T1"), (2, "src1.md", "T2"), (3, "src0.md", "T3")],
    )
)

# 9 字符串数字
results.append(run_case("9 字符串数字", '["1","2"]', expect=HITS[:3]))

# 10 部分列表 [5] → 只有 1 条
results.append(run_case("10 部分列表 [5]", "[5]", expect=[(1, "src0.md", "T5")]))

# 附加 11：全量倒序
results.append(
    run_case(
        "11 全量倒序",
        "[10,9,8,7,6,5,4,3,2,1]",
        expect=[(1, "src1.md", "T10"), (2, "src0.md", "T9"), (3, "src1.md", "T8")],
    )
)

print()
print(f"=== 结果: {sum(results)}/{len(results)} ===")
