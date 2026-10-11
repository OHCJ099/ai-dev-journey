"""教练验收脚手架：e2e 串联与坏输入验证；read 只读重开验证。

这是验证代码，不是学员编写的业务代码，也不作为独立能力证据。
每次 e2e 在独立进程运行，只清 demo_w13 的专用 scratch 练习索引。
"""

import contextlib
import importlib
import io
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))
demo = importlib.import_module("demo_w13")
demo.enable_offline()


def reject_embedding(_text: str) -> list[float]:
    raise AssertionError("坏输入应在开始计算向量前被拒绝")


def verify_e2e() -> None:
    state = {}
    calls = []
    original_query = demo.query_lab.query_index

    def observed_query(collection, question, k=3, source=None):
        hits = original_query(collection, question, k=k, source=source)
        calls.append((source, len(hits)))
        return hits

    def capture(frame, event, _arg):
        if frame.f_code is demo.main.__code__ and event == "return":
            state.update(frame.f_locals)

    demo.query_lab.query_index = observed_query
    sys.setprofile(capture)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            demo.main()
    finally:
        sys.setprofile(None)
        demo.query_lab.query_index = original_query

    assert calls == [
        (demo.SAMPLE_A.name, 3),
        (demo.SAMPLE_B.name, 1),
        (demo.SAMPLE_A.name, 0),
        (demo.SAMPLE_B.name, 1),
    ], calls
    assert len(state["before"]["ids"]) == 3
    assert state["after"]["ids"] == [f"{demo.SAMPLE_A.name}-1"]
    expected = demo.splitter.split_text(
        demo.loader.load_document(demo.UPDATED_A)["text"],
        demo.ingest.CHUNK_SIZE,
        demo.ingest.OVERLAP,
    )
    assert state["after"]["documents"] == expected
    assert state["deleted"] == 1
    collection = state["collection"]
    assert not collection.get(where={"source": demo.SAMPLE_A.name})["ids"]
    remaining = collection.get(where={"source": demo.SAMPLE_B.name})
    assert remaining["ids"]
    assert remaining["ids"] == state["a_before"]["ids"]
    assert remaining["documents"] == state["a_before"]["documents"]
    print("上传后限定检索：差旅报销制度.md=3条，信息安全制度.md=1条")
    print("覆盖更新：报销3块变1块，旧尾块消失，正文匹配修订版")
    print("删除后限定检索：差旅报销制度.md=0条，信息安全制度.md=1条")
    print("保留来源：ID和正文不变")

    original_embed = demo.ingest.embed
    demo.ingest.embed = reject_embedding
    try:
        for filename in ("空文件.md", "未知格式.txt"):
            path = PROJECT_DIR / "samples" / filename
            before_count = collection.count()
            before_data = collection.get()
            assert before_count > 0, "必须在已有数据的库上验证不污染"
            try:
                demo.ingest.ingest_file(path, demo.INDEX_PATH)
            except ValueError as error:
                after_count = collection.count()
                after_data = collection.get()
                assert after_count == before_count
                for key in ("ids", "documents", "metadatas"):
                    assert after_data[key] == before_data[key], key
                print(
                    f"{filename}：ValueError；count {before_count} -> {after_count}；"
                    "ID/正文/来源不变；未进入向量计算"
                )
                print(f"错误原文：{error}")
            else:
                raise AssertionError(f"{filename} 未被拒绝")
    finally:
        demo.ingest.embed = original_embed


def verify_read() -> None:
    collection = demo.index_store.open_index(demo.INDEX_PATH)
    report = demo.query_lab.query_index(
        collection, "报销如何提交？", source=demo.SAMPLE_A.name
    )
    security = demo.query_lab.query_index(
        collection, "账号使用有哪些要求？", source=demo.SAMPLE_B.name
    )
    expected = demo.splitter.split_text(
        demo.loader.load_document(demo.SAMPLE_B)["text"],
        demo.ingest.CHUNK_SIZE,
        demo.ingest.OVERLAP,
    )
    assert report == []
    assert len(security) == 1
    assert security[0][0] == demo.SAMPLE_B.name
    assert security[0][1] == expected[0]
    assert collection.count() == 1
    print("独立进程只读重开：报销0条，信息安全1条，总count=1")
    print("删除未复活，保留正文匹配样张；未清库、未重新入库")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"e2e", "read"}:
        print("用法：uv run python projects/rag-kb/archive/w13_verify.py <e2e|read>")
        raise SystemExit(1)
    if sys.argv[1] == "e2e":
        verify_e2e()
    else:
        verify_read()
