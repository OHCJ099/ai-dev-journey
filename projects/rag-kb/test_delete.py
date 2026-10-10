"""测试 delete_source：删除某来源后，库里到底变成什么样。"""

import sys
from pathlib import Path

from index_store import add_chunks, delete_source, open_index

# 练习库放 scratch，别动正式语料
INDEX_PATH = Path("D:/Hermes/cache/scratch/w13/delete_lab")

# 离线夹具向量 —— 不花钱、不代表语义
FAKE_VECTORS = [[0.1, 0.2, 0.3], [0.9, 0.8, 0.7], [0.4, 0.5, 0.6]]


def do_delete():
    # ★ 1. 打开库（先清空重来，避免上次残留）
    collection = open_index(INDEX_PATH)

    delete_source(collection, "测试A")
    delete_source(collection, "测试B")
    # ★ 2. 打底：写两份来源，A 有 3 块、B 有 2 块（用 add_chunks + FAKE_VECTORS）
    add_chunks(collection, "测试A", ["哈哈", "haha", "aaa"], FAKE_VECTORS)
    add_chunks(collection, "测试B", ["哈哈", "haha"], FAKE_VECTORS[:2])
    # ★ 3. 打印打底后 count
    print("===删除前===")
    A_count = collection.get(where={"source": "测试A"})
    B_count = collection.get(where={"source": "测试B"})
    print(f"测试A: {A_count['ids']}\n测试B: {B_count['ids']}")
    # ★ 4. 删 A → 打印返回值（应该是整数 3）
    A_delete = delete_source(collection, "测试A")
    print(f"已删除[{A_delete}]个 测试A")
    # ★ 5. 打印删后 count（应该只剩 B 的 2 条）
    print("===删除后===")
    A_count1 = collection.get(where={"source": "测试A"})
    B_count1 = collection.get(where={"source": "测试B"})
    print(f"测试A: {A_count1['ids']}个\n测试B: {B_count1['ids']}个")
    # ★ 6. 读回 A（get(where=)）→ 应该是 []
    print(f"读回A: {collection.get(where={'source': '测试A'})['ids']}")
    # ★ 7. 读回 B → 一条不少
    print(f"读回B: {collection.get(where={'source': '测试B'})['ids']}")
    # ★ 8. 删不存在的来源 → 返回 0、不崩
    delete = delete_source(collection, "???")
    print(delete)


def do_read():
    collection = open_index(INDEX_PATH)
    A = collection.get()
    print(A["ids"])
    print("A:", collection.get(where={"source": "测试A"})["ids"], "→ 应为 []")
    print("B:", collection.get(where={"source": "测试B"})["ids"], "→ 应有 2 条")


if __name__ == "__main__":
    # ★ 照 test_ingest.py 的 argv 写法，支持 delete / read 两个子命令
    if len(sys.argv) != 2 or sys.argv[1] not in {"delete", "read"}:
        print(
            "正确用法: uv run python D:/dev/ai-dev-journey/projects/rag-kb/test_delete.py <delete / read>"
        )
    elif sys.argv[1] == "delete":
        do_delete()
    else:
        do_read()
