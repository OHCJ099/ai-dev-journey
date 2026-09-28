# rag-kb · 企业制度知识库（W9 雏形）

RAG 知识库问答系统的**文档处理层**：把 `data/` 下的企业制度文档（`.md` / `.txt`）加载 → 清洗 → 切成 chunk，为后续向量化与检索做准备。

## 怎么跑

```powershell
uv run python projects\rag-kb\loader.py           # 加载 + 清洗：打印每份文档清洗前后字符数
uv run python projects\rag-kb\run_experiments.py  # 切分对比实验：chunk_size / overlap 各三档
```

## 结构

- `data/` — 语料：5 份企业制度文档（员工手册节选 / 考勤 / 报销 / 请假 / 安全规范）
- `loader.py` — `load_documents()` 读目录 + `clean_text()` 清洗（统一换行 / 去每行首尾空白 / 压缩连续空行）
- `splitter.py` — `split_text(text, chunk_size, overlap)` 固定字数切分（纯字符串切片手写，不引库）
- `experiments.md` — 参数对比实验记录（chunk_size 200/500/1000、overlap 0/50/100，含切断案例）
