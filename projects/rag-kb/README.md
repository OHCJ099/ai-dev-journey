# rag-kb · 企业制度知识库（项目②，毕设 #91 同源）

RAG 知识库问答系统。当前进度：**文档处理 ✅ W9 → 向量化与检索 ✅ W10 → 拼上下文与问答 🔄 W11（进行中）**。

## 文件地图（找函数先看这张表）

| 文件 | 关键函数 / 内容 | 同目录依赖 | 状态 |
|---|---|---|---|
| `loader.py` | `load_documents()` 读 `data/`；`clean_text()` 清洗（统一换行 / 去首尾空白 / 压空行） | — | ✅ W9 |
| `splitter.py` | `split_text(text, chunk_size, overlap)` 切块 + 参数守卫 | `loader`（演示用） | ✅ W9 |
| `run_experiments.py` | 切分对比实验（chunk_size / overlap 各三档） | `loader` `splitter` | ✅ W9 |
| `experiments.md` | 实验记录：数字与结论都在这（W12 评估集要引用） | — | ✅ W9–W10 |
| `embed_test.py` | 最小脚本：DashScope `text-embedding-v4` 拿一条 1024 维向量 | — | ✅ W10 |
| `retriever.py` | `embed()` 向量化 / `cos_sim()` 余弦 / `retrieve()` 手写 top-k（含 `min_score`） | `loader` `splitter` | ✅ W10 |
| `chroma_store.py` | `build_collection()` Chroma 建库 + 查询（与手写版对照 10/10 一致） | `loader` `splitter` `retriever` | ✅ W10 |
| `qa.py` | `build_index()` / `retrieve_hits()` / `build_context()` / `ask()`：检索 → 拼材料 → DeepSeek 回答 | `loader` `splitter` `retriever` | 🔄 W11 |
| `reference/` | 参考答案（卡住 25 分钟以上再看）：`loader_reference.py` / `splitter_reference.py` | — | — |
| `data/` | 语料：5 份企业制度 `.md`（员工手册节选 / 考勤 / 报销 / 请假 / 安全） | — | ✅ W9 |

**依赖关系**（`embed()` 是唯一的向量化入口，`chroma_store` / `qa` 都复用它）：

```
loader.py        （最底层，无内部依赖）
splitter.py      ← loader
retriever.py     ← loader, splitter
chroma_store.py  ← loader, splitter, retriever
qa.py            ← loader, splitter, retriever
```

> 脚本之间用「同目录直呼其名」互相 import（如 `from loader import load_documents`）—— Python 会把脚本所在目录加进模块搜索路径，所以不用写包名。

## 在 VS Code 里快速找代码

- 光标放函数名上按 **`F12`** → 跳到定义处（例：`from retriever import embed` 里的 `embed` 就跳去 `retriever.py`）
- **`Ctrl+T`** → 全仓库搜函数名 / 类名
- **`Ctrl+Shift+O`** → 列出当前文件所有函数，直接跳
- 看 import 行就知道函数住哪：`from splitter import split_text` → `split_text` 在 `splitter.py`

## 怎么跑（在仓库根目录）

```powershell
uv run python projects\rag-kb\loader.py           # 加载 + 清洗（免 key）
uv run python projects\rag-kb\run_experiments.py  # 切分对比实验（免 key）
uv run python projects\rag-kb\embed_test.py       # 单条向量 1024 维
uv run python projects\rag-kb\retriever.py        # 手写检索 top-k
uv run python projects\rag-kb\chroma_store.py     # Chroma 检索对照
uv run python projects\rag-kb\qa.py               # 端到端问答（W11）
```

> 需要 key 的：`embed_test` / `retriever` / `chroma_store` / `qa`（`.env`：DashScope 向量化 + DeepSeek 生成）。
