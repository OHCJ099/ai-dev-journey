"""W13 命令行串联练习：离线假向量，只验证数据流，不验证语义质量。"""

import shutil

import config
import index_store
import ingest
import loader
import query_lab
import splitter

LAB_DIR = config.LAB_DIR / "demo_w13"
INDEX_PATH = LAB_DIR / "index"
SAMPLE_A = LAB_DIR / "修订前" / "差旅报销制度.md"
UPDATED_A = LAB_DIR / "修订后" / "差旅报销制度.md"
SAMPLE_B = LAB_DIR / "信息安全制度.md"


def fake_embed(text: str) -> list[float]:
    """教学夹具：不访问网络，所有文本都返回相同的三维假向量。"""
    return [0.1, 0.2, 0.3]


def enable_offline() -> None:
    """同时替换入库和查询模块各自使用的 embed。"""
    ingest.embed = fake_embed
    query_lab.embed = fake_embed


def main() -> None:
    """在这里串联上传 → 查询 → 覆盖更新 → 删除 → 再查询。

    待实现：
    - 样张只写在 LAB_DIR 下，准备两份来源；旧版必须切出至少两块。
    - 报量后调用已有入库函数，打印实际写入数。
    - 按来源查询并展示正文；假向量不用于判断语义排名。
    - 使用修订后同名制度覆盖入库，读回 ID 和正文证明旧尾块消失。
    - 删除其中一份，确认它不再召回，另一份的内容保持。
    - 后续另起进程重开同一个库，只读验证，不重新入库。
    """
    shutil.rmtree(INDEX_PATH, ignore_errors=True)

    SAMPLES = [SAMPLE_A, SAMPLE_B]
    for SAMPLE in SAMPLES:
        doc = loader.load_document(SAMPLE)
        chunks = splitter.split_text(doc["text"], ingest.CHUNK_SIZE, ingest.OVERLAP)
        print(f"{doc['source']}: 预计入库数[{len(chunks)}]块")

        chunks_count = ingest.ingest_file(SAMPLE, INDEX_PATH)
        print(f"实际写入[{chunks_count}]块")

        print()

    collection = index_store.open_index(INDEX_PATH)
    count = collection.count()
    print(f"当前总数为[{count}]块\n")

    print("=======限定查询=======")

    for SAMPLE in SAMPLES:
        anwsers = query_lab.query_index(
            collection, "请假流程是什么？", k=3, source=SAMPLE.name
        )
        print(f"返回条数: [{len(anwsers)}]")
        print(f"本轮限定: [{SAMPLE.name}]")
        for anwser in anwsers:
            print(f"来源: {anwser[0]} \n正文: {anwser[1][:30]}\n")
        print("=======本轮结束=======")

    before = collection.get(where={"source": "差旅报销制度.md"})
    a_before = collection.get(where={"source": SAMPLE_B.name})
    print(f"更新前ids: {before['ids']} 更新前正文: {before['documents']}")
    count = ingest.ingest_file(UPDATED_A, INDEX_PATH, True)
    print(f"已插入[{count}]条数据")
    after = collection.get(where={"source": "差旅报销制度.md"})
    print(f"更新后ids: {after['ids']} 更新后正文: {after['documents']}")
    b_before = collection.get(where={"source": SAMPLE_B.name})
    if (
        a_before["ids"] == b_before["ids"]
        and a_before["documents"] == b_before["documents"]
    ):
        print("信息安全制度.md 无变化")

    deleted = index_store.delete_source(collection, SAMPLE_A.name)
    print(f"删除[{deleted}]条数据")

    for SAMPLE in SAMPLES:
        anwsers = query_lab.query_index(
            collection, "请假流程是什么？", k=3, source=SAMPLE.name
        )
        print(f"{anwsers},{len(anwsers)}")


if __name__ == "__main__":
    enable_offline()
    main()
