"""W12 第 1 件：评估集跑分 —— 读 eval_questions.md → 逐题检索 top-3 → 打印 → 统计命中。

跑法（仓库根目录）：uv run python projects/rag-kb/eval_run.py
流程：① 先跑一次看每题召回的片段 ② 在 eval_questions.md 的「判定」列逐题填写
      ③ 再跑一次，输出「开发集召回 X/Y」统计
"""

from pathlib import Path

from loader import load_documents
from qa import build_index, retrieve_hits

DATA_DIR = Path(__file__).parent / "data"
EVAL_FILE = Path(__file__).parent / "eval_questions.md"
K = 3
RUN_SETS = ("开发",)  # 留出集调参结束前不跑：跑过就等于把它当开发集用了


def load_eval(path: Path) -> list[dict[str, str]]:
    """读评估集 md 表格 → 每题一个 dict。

    一行长这样：| 1 | 开发 | 有答案 | 问题文本 | 请假制度.md | 要点 | 命中 |
    解析：去掉行首尾的 |，再按 | 切开 —— cells[0] 是编号、cells[1] 是集，依此类推。
    空行 / 表头 / 分隔行（|---|）/ 还没填问题的行，都会被跳过。
    """
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or not cells[0] or cells[0].startswith("-"):
            continue
        if cells[0] == "编号" or not cells[3]:  # 表头 / 问题还没填
            continue
        while len(cells) < 7:  # 判定列留空时行尾少一格，补上
            cells.append("")
        rows.append(
            {
                "编号": cells[0],
                "集": cells[1],
                "题型": cells[2],
                "问题": cells[3],
                "期望来源": cells[4],
                "期望要点": cells[5],
                "判定": cells[6],
            }
        )
    return rows


def run_eval(questions: list[dict[str, str]], collection) -> None:
    """逐题检索 + 打印；然后按「判定」列统计。"""
    for q in questions:
        print(
            f"\n== [{q['编号']}] {q['问题']} ==  期望来源：{q['期望来源']}（{q['题型']}）"
        )
        # TODO（你写 · 第 1 处）：调 retrieve_hits 拿 top-3，逐条打印「来源 + 完整片段文本」。
        hit = retrieve_hits(collection, q["问题"], k=K)
        for h in hit:
            #  提示：hits 每条是 (编号, 来源, 文本)；判断题要读完整文本，别只打前 30 字。
            print(f"[{h[0]}] 来源: {h[1]}\n{h[2]}")

    fen_mu = 0
    fen_zi = 0
    no_anwser = []
    not_checked = []
    # TODO（你写 · 第 2 处）：统计并打印（读「判定」列）：
    for q in questions:
        #  - 开发集召回：分母 = 题型为「有答案」或「部分可答」的题数；分子 = 判定为「命中」的题数
        if q["题型"] == "有答案" or q["题型"] == "部分可答":
            fen_mu += 1
            if q["判定"] == "命中":
                fen_zi += 1
            elif q["判定"] == "未命中":
                continue
            else:
                not_checked.append(q["编号"])
        if q["题型"] == "无答案":
            no_anwser.append(q["编号"])
    #  - 输出形如：开发集召回 X/Y
    #  - 无答案题不进分母，单独列出它们的编号；没填判定的题也单独提醒
    print(
        f"开发集召回：{fen_zi}/{fen_mu}\n无答案编号：{no_anwser}\n待判定编号：{not_checked}"
    )


def main() -> None:
    questions = load_eval(EVAL_FILE)
    print(f"评估集共 {len(questions)} 题（本次跑：{'/'.join(RUN_SETS)}集）")
    if not questions:
        print("评估集还是空的：先把 eval_questions.md 里 20 题填上。")
        return

    questions = [q for q in questions if q["集"] in RUN_SETS]

    docs = load_documents(DATA_DIR)
    print("正在建索引（每个块一次 embedding 调用，约 1 分钟）……")
    collection = build_index(docs)

    run_eval(questions, collection)


if __name__ == "__main__":
    main()
