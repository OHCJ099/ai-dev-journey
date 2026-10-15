# projects/rag-kb/max_key_practice.py
# W15 前置加练：把「for 循环找最大值」改成 max(key=) 惯用写法
# 对照诊断题 1（10-14）：原写法 7 行 + `max = 0` 初始值隐患 + 覆盖内置 max

docs = [
    {"source": "考勤制度.md", "blocks": 11},
    {"source": "请假制度.md", "blocks": 13},
    {"source": "报销制度.md", "blocks": 12},
]

print(max(docs, key=lambda d: d["blocks"])["source"])

print([d for d in docs if d["blocks"] > 10])
