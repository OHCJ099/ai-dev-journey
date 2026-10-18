# RAG 知识库：4 个失败案例

> 每条四行：现象 → 根因 → 修法 → 怎么验证的。全部为项目 ②（`projects/rag-kb/`）真实发生过的缺陷，
> 不是教科书举例。验证行贴的是实跑命令与输出，可复现。

## 案例 1：同名传坏文件会毁掉好文件

**现象**
同名上传一份坏文件（如纯空白 md）→ 接口返回 400，但**磁盘上的旧好文件已被覆盖**，删文件后连原本的
好内容一起没了；更坏的是**索引里还存着旧正文** —— 磁盘与索引不一致，检索用的是旧版、磁盘显示的是空白。

**根因**
`api.py` 的顺序是「先 `write_bytes` 落盘 → 再调 `ingest_file` 校验」。`ingest_file` 内部又调
`load_document(磁盘路径)` 读盘解析，**校验用的已经是覆盖后的坏文件**；失败后「删掉刚写的文件」把原本的
好文件一起删了。

**修法**
把解析提到落盘之前，且纯内存进行：`loader.parse_bytes(filename, content)` 先校验（失败抛 `ValueError`
→ 400，**不碰磁盘**），通过后才 `write_bytes` + `ingest_file`。

**怎么验证的**
```
# ① 先传好文件
curl -X POST /upload -F "file=@<好文件>"     → {"source":"<文件名>","blocks":1}
cat uploads/<文件名>                          → AAAA 原始好文件内容
索引 get(where={"source":"<文件名>"})         → 1 块，正文 = AAAA 原始内容

# ② 同名传纯空白（坏文件）
curl -X POST /upload -F "file=@<纯空白文件>"  → {"detail":"文件内容为空: <文件名>"}  HTTP=400
cat uploads/<文件名>                          → 仍是 AAAA（未被覆盖）
索引 get(where={"source":"<文件名>"})         → 仍是 1 块，正文 = AAAA
```
**关键：磁盘和索引两侧都要验，只验磁盘不够** —— 这个 bug 最坏的结果是两侧不一致。

## 案例 2：护栏丢失，`k=0` 一路打到 Chroma

**现象**
`POST /query` 传 `k=0`（或负数）时，接口返回 **500 裸崩**，而不是明确的 4xx。前端一旦传了非法 `k`
（或调用方漏传、传字符串），整个接口挂掉。

**根因**
`api_models.py` 的 `Field(default=3, ge=1, le=10)` 被换成了裸 `k: int = TOP_K`，`ge/le` 校验护栏全丢。
`k=0` 于是通过 Pydantic 一路传到 `collection.query(n_results=0)`，Chroma 抛
`TypeError: Number of requested results 0, cannot be negative, or zero.`，FastAPI 没接住 → 500。

**注意**：`Field` 抛出的是 **`ValidationError`**（Pydantic），`TypeError` 是 **Chroma** 抛的。
**护栏在哪一层，决定报错是 422 还是 500**：Pydantic 拦下 → 422；拦不住 → 到 Chroma → 500。

**修法**
`api_models.py` 恢复 `k: int = Field(default=TOP_K, ge=1, le=10)`。

**怎么验证的**
```
curl -X POST /query -d '{"question":"<问题>","k":0}'    → 422
curl -X POST /query -d '{"question":"<问题>","k":-5}'   → 422
curl -X POST /query -d '{"question":"<问题>","k":100}'  → 422
curl -X POST /query -d '{"question":"<问题>"}'          → 200，引用 3 条（默认 TOP_K=3）
```

## 案例 3：同一个值散在 6 个文件里

**现象**
切块参数 `500 / 50` 在 `chroma_store.py` / `ingest.py` / `qa.py` / `retriever.py` / `splitter.py` /
`test_ingest.py` 各写一遍。想调参得改 6 处，**改一处漏一处**：漏改的模块仍按旧值切块，同一份文档在
上传链和问答链切出不同块数，检索结果对不上。`TOP_K` 同理（`config.py` 的 `TOP_K=3` 与
`api_models.py` 的 `le=10` 是同一规则写两处）。

**根因**
没有单一权威定义。这是「配置散落」的典型：同一个业务规则被复制粘贴到多个模块，复制之后各自独立演化。

**修法**
新建 `projects/rag-kb/config.py` 作为唯一权威定义（`CHUNK_SIZE` / `OVERLAP` / `TOP_K` /
单价常量 / 日志路径），6 处硬编码逐处改为 `from config import ...`。
**为什么用 `config.py` 而不是 `from ingest import CHUNK_SIZE`**：`ingest.py` 已经 `import splitter`，
反向 import 会循环引用。

**怎么验证的**
```
# ① 改成和原来不同的值（500→300、50→5），否则改了等于没改
sed -i 's/CHUNK_SIZE = 500/CHUNK_SIZE = 300/' config.py
# ② 6 个模块是否都跟着变
chroma_store   CHUNK_SIZE=300 OVERLAP=5
ingest         CHUNK_SIZE=300 OVERLAP=5
qa             CHUNK_SIZE=300 OVERLAP=5
retriever      CHUNK_SIZE=300 OVERLAP=5
api_models     TOP_K=3
query_lab      TOP_K=3
# ③ 块数是否真的按新参数算
chunk_size=300 overlap=5   -> 10 块
chunk_size=500 overlap=50  -> 7 块
# ④ 恢复 500/50 后再确认一次
```

## 案例 4：假向量库与真向量库共用一个目录

**现象**
离线调试（`api_lab`，3 维假向量）跑完，切到真实服务（`api`，1024 维真向量）后第一次 `/query` 直接
**500 裸崩**：

```
chromadb.errors.InvalidArgumentError:
Collection expecting embedding with dimension of 3, got 1024
```

**根因**
`api.py:21` 的 `INDEX_PATH` 被 `api_lab` 和 `api` 共用。Chroma 的 collection 在**创建时**就固定了
向量维度（由第一批写入的向量决定），后续写入/查询必须同维度。假向量 3 维、真向量 1024 维 → 直接拒绝。

**这是「配置共享但语义不同」的典型**：路径是同一个字符串，但两边要求的**数据形状**不同。

**修法**
离线入口与真实入口用**不同的索引目录**（例如由环境变量或入口模块各自指定），不要共用同一个
`INDEX_PATH`。**注意这不是「删掉重建」能根治的** —— 只要两个入口仍指向同一路径，下次还会撞。

**怎么验证的**
```
# 离线跑完
uv run uvicorn api_lab:app --port 8770 ...   → /query 200（假向量 3 维）
# 切真实服务
uv run uvicorn api:app --port 8772 ...       → /query 500
# 服务端 traceback
chromadb.errors.InvalidArgumentError: Collection expecting embedding with dimension of 3, got 1024
```

## 附：一条「假替身掩盖真实差异」的教训（10-17）

`api_lab.py` 的 `fake_create` 把 `usage` 写死成 `prompt_tokens=10 / completion_tokens=20`，于是
「`k` 变大 → 材料变多 → `prompt_tokens` 该变大」这条验收在离线状态下**根本测不出来** —— 三次查询的
日志数字完全一样。

**教训**：假替身（stub）只证明「接线通了」，不能证明「数值正确」。凡是要验数值关系的验收，必须用真实
调用，或者让假替身按输入计算返回值。写验收条件时先问一句：**这个数字是从哪来的？**