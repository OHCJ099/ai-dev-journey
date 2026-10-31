"""扫描教练写给学员看的文字，找出「不像人话」的句子。

只查能被机器判定、且有明确改法的四类问题：

R1 空指代     「出错后」「报错后」前面没有说清是哪种错
R2 结果无主   「3 passed」前后 40 字内没有测试文件或命令
R3 跨天无内容 「昨天那两问」「上次那个」要求读者自己翻记录
R4 隐喻       「缺口」「埋雷」「坏了能查」

用法：
    uv run python tools/check_language.py            # 只看统计
    uv run python tools/check_language.py -v         # 逐条列出
    uv run python tools/check_language.py --jargon   # 加查黑话动词（误报较多）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 现在生效、子教练每次开工都会读的文字
ACTIVE = [
    ".hermes.md",
    "handbook/00-怎么用这套体系.md",
    "handbook/07-当前任务指令.md",
]

# 最近两个日报也算（子教练会照着写）
RECENT_LOGS = 2

# R1：这些词前面必须已经交代过是哪种错
VAGUE_ERROR = re.compile(r"(出错|报错)后")

# R2：「N passed / N failed」附近要有文件或命令
TEST_RESULT = re.compile(r"\d+\s*(passed|failed)")
CONTEXT_HINT = re.compile(r"(\.py|week\d\d|practice/|projects/|contacts/)")

# R3：跨天引用必须自带内容，不能只说「昨天那个」
VAGUE_RECALL = re.compile(
    r"(昨天|前天|上次|刚才|之前)[^，。；：]{0,6}(那|这)"
    r"|(昨天|前天|上次|刚才|之前)(讲|说|问|提|留|写)的"
)

# R4：隐喻代替了机制描述
METAPHOR = [
    "坏了能查",
    "埋雷",
    "缺口",
    "打地鼠",
    "喂给",
    "扛住",
    "兜住",
]

# R5（可选）：把动作写成私有名词
JARGON = [
    "收进",
    "收口",
    "打底",
    "拉齐",
    "销项",
    "挂账",
    "颗粒度",
    "抓手",
]

SUGGEST = {
    "R1": "说清是哪种错：静态检查？服务启动？请求上游返回 401？还是连不上？",
    "R2": "点名是哪个文件、哪条命令：「pytest week01/contacts/ → 3 个通过」；只写 pytest 不算点名。",
    "R3": "把内容写出来，别让读者翻记录：「print 只打到终端，logger.info 带时间、级别、模块名」。",
    "R4": "换成机制描述：「报错时看不出是哪一步失败的」。",
    "R5": "换成普通动词：「把 X 写进 config.py」而不是「收进 config」。",
}


def quoted_positions(line: str) -> list[tuple[int, int]]:
    """返回被「」括起来的区间，这些是在举反例，不算违规。"""
    spans = []
    for m in re.finditer(r"「[^」]*」", line):
        spans.append((m.start(), m.end()))
    return spans


def is_quoted(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(a <= pos < b for a, b in spans)


def scan_line(line: str, jargon: bool) -> list[tuple[str, str]]:
    """返回这一行命中的 (规则号, 命中的原文)。"""
    hits: list[tuple[str, str]] = []
    spans = quoted_positions(line)

    for m in VAGUE_ERROR.finditer(line):
        if is_quoted(m.start(), spans):
            continue
        # 前面 20 字内已经提到具体错误类型就不算
        head = line[max(0, m.start() - 20) : m.start()]
        if not re.search(
            r"(静态|启动|超时|连接|鉴权|401|403|404|429|500|502|503|异常)", head
        ):
            hits.append(("R1", m.group(0)))

    for m in TEST_RESULT.finditer(line):
        if is_quoted(m.start(), spans):
            continue
        window = line[max(0, m.start() - 40) : m.end() + 40]
        if not CONTEXT_HINT.search(window):
            hits.append(("R2", m.group(0)))

    for m in VAGUE_RECALL.finditer(line):
        if is_quoted(m.start(), spans):
            continue
        hits.append(("R3", m.group(0)))

    for word in METAPHOR:
        if word in line and not is_quoted(line.index(word), spans):
            hits.append(("R4", word))

    if jargon:
        for word in JARGON:
            if word in line and not is_quoted(line.index(word), spans):
                hits.append(("R5", word))

    return hits


def collect_targets(all_files: bool) -> list[str]:
    names = list(ACTIVE)
    logs = sorted((ROOT / "logs").glob("*.md"))
    names += [f"logs/{p.name}" for p in logs[-RECENT_LOGS:]]
    if all_files:
        names += ["ROADMAP.md", "progress.md"]
        names += [
            f"handbook/{p.name}" for p in sorted((ROOT / "handbook").glob("*.md"))
        ]
        names += [f"logs/{p.name}" for p in logs]
        names = list(dict.fromkeys(names))
    return names


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true", help="逐条打印命中的句子")
    ap.add_argument(
        "--all", action="store_true", help="连历史日报和台账一起查（历史遗留不算错）"
    )
    ap.add_argument("--jargon", action="store_true", help="加查黑话动词（误报较多）")
    args = ap.parse_args()

    total = 0
    per_rule: dict[str, int] = {}
    per_file: dict[str, int] = {}

    for name in collect_targets(args.all):
        path = ROOT / name
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            hits = scan_line(line, args.jargon)
            if not hits:
                continue
            per_file[name] = per_file.get(name, 0) + len(hits)
            for rule, frag in hits:
                per_rule[rule] = per_rule.get(rule, 0) + 1
                total += 1
                if args.verbose:
                    print(f"{name}:{lineno} {rule} 「{frag}」")
                    print(f"    → {SUGGEST[rule]}")

    print()
    print(f"合计 {total} 处")
    for rule in sorted(per_rule):
        print(f"  {rule} {per_rule[rule]:4d} 处")
    if per_file:
        print()
        for name, n in sorted(per_file.items(), key=lambda x: -x[1]):
            print(f"  {n:4d}  {name}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
