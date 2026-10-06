"""W13 首日：index_store 的测试脚本 —— 用两个进程证明「重开索引数据还在」。

跑法（仓库根目录，两条命令分别是两个进程）：
  uv run python projects/rag-kb/test_index_store.py write
  uv run python projects/rag-kb/test_index_store.py read

注意：下面的向量是**离线夹具**（固定几位数字，专门标成假的）。
它只用来验证「数据能不能写进去、重开后还在、来源和 ID 对不对」，
不代表真实语义召回效果 —— 所以不调用任何 embedding 服务、也不花 token。
"""

import shutil
import sys
from pathlib import Path

from index_store import add_chunks, open_index

# 练习库放在 scratch 专用子目录，不写正式语料、不写生产索引。
INDEX_PATH = Path("D:/Hermes/cache/scratch/w13/index_store_lab")

FAKE_VECTORS = [[0.1, 0.2, 0.3], [0.9, 0.8, 0.7]]


def do_write() -> None:
    """进程一：打开索引 → 写入两份来源 → 打印库里的 id。"""
    collection = open_index(INDEX_PATH)

    print("写入前 count:", collection.count())

    add_chunks(
        collection,
        source="报销制度.md",
        chunks=["第一条 报销范围。", "第二条 报销流程。"],
        embeddings=FAKE_VECTORS[:2],
    )
    add_chunks(
        collection,
        source="考勤制度.md",
        chunks=["迟到一次扣五十。"],
        embeddings=FAKE_VECTORS[:1],
    )

    print("写入后 count:", collection.count())
    print("库里的 id:", collection.get()["ids"])


def do_read() -> None:
    """进程二：重新打开同一个 path → 用 get() 读回上一进程写入的东西。

    这一进程**不调用 add_chunks**：读得到 = 数据落在磁盘上，不是内存残留。
    """
    collection = open_index(INDEX_PATH)

    print("重开进程 count:", collection.count())

    data = collection.get()
    print("ids:", data["ids"])
    print("documents:", data["documents"])
    print("metadatas:", data["metadatas"])

    # 按来源读回其中一份，确认 source 元数据没丢。
    print(
        "只读报销制度.md:",
        collection.get(where={"source": "报销制度.md"})["documents"],
    )


def do_check() -> None:
    """破坏性测试：四种坏输入各包各的 try，验「抛错的同时库没被动过」。

    每次从空库起步（rmtree），否则「打底」那一步会先撞上重复来源。
    """
    shutil.rmtree(INDEX_PATH, ignore_errors=True)
    collection = open_index(INDEX_PATH)

    # 打底：两份正常来源，后面所有坏输入都拿它俩当参照。
    add_chunks(
        collection,
        source="报销制度.md",
        chunks=["第一条 报销范围。", "第二条 报销流程。"],
        embeddings=FAKE_VECTORS[:2],
    )
    add_chunks(
        collection,
        source="考勤制度.md",
        chunks=["迟到一次扣五十。"],
        embeddings=FAKE_VECTORS[:1],
    )
    print("打底后 count:", collection.count())

    # 四种坏输入，每行 = (情况名, source, chunks, embeddings)
    cases = [
        ("重复来源再写一次", "考勤制度.md", ["迟到一次扣五十。"], FAKE_VECTORS[:1]),
        ("混入纯空白块", "空格块.md", ["第一条正常", "   "], FAKE_VECTORS[:2]),
        ("空向量批次", "空向量.md", ["测试块"], []),
        (
            "chunks 与 embeddings 长度不匹配",
            "长度不符.md",
            ["测试块1", "测试块2"],
            FAKE_VECTORS[:1],
        ),
    ]

    for name, source, chunks, embeddings in cases:
        before = collection.count()
        try:
            add_chunks(collection, source, chunks, embeddings)
            print(f"{name} | 没抛错（该拦的没拦住）")
        except ValueError as error:
            print(
                f"{name} | 改前 {before} | 改后 {collection.count()} | ValueError: {error}"
            )

    print("最终 count:", collection.count())


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in {"write", "read", "check"}:
        print(
            "用法：uv run python projects/rag-kb/test_index_store.py <write|read|check>"
        )
        raise SystemExit(1)

    if sys.argv[1] == "write":
        do_write()
    elif sys.argv[1] == "read":
        do_read()
    else:
        do_check()
