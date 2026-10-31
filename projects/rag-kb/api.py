import logging
from pathlib import Path
from time import monotonic

import config
import index_store
import ingest
import loader
import qa
import query_lab
from api_models import QueryRequest
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
)

app = FastAPI()

UPLOAD_PATH = config.UPLOAD_DIR
INDEX_PATH = config.INDEX_PATH

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)

logger = logging.getLogger(__name__)

# 限流：同一个 IP，60 秒内最多 5 次查询
WINDOW_SECONDS = 60
MAX_PER_WINDOW = 5
_buckets: dict[str, tuple[float, int]] = {}


def rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = monotonic()
    start, count = _buckets.get(ip, (now, 0))
    if now - start >= WINDOW_SECONDS:  # 条件 1：窗口已经过期，重新开始计数
        start, count = now, 0
    count += 1
    _buckets[ip] = (start, count)
    if count > MAX_PER_WINDOW:  # 条件 2：超过上限，拒绝
        raise HTTPException(status_code=429, detail="请求太频繁，请稍后再试")


# 接收上传文件，保存后调用已有入库函数。
@app.post("/upload")
async def upload(file: UploadFile = File(...)):  # noqa: B008 -- FastAPI 上传字段声明，不是可变默认容器。
    content = await file.read()
    if file.filename is None or file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="文件名不能为空")
    file_path = UPLOAD_PATH / Path(file.filename).name

    try:
        loaded_text = loader.parse_bytes(file_path.name, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

    file_path.write_bytes(content)

    try:
        count = ingest.ingest_file(file_path, INDEX_PATH, True, loaded_text=loaded_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"source": file_path.name, "blocks": count}


@app.get("/sources")
async def get_collection():
    counts: dict[str, int] = {}
    d = []

    collection = index_store.open_index(INDEX_PATH)
    result = collection.get()
    for i in result["metadatas"] or []:
        source = str(i["source"])
        counts[source] = counts.get(source, 0) + 1

    for s, blocks in counts.items():
        d.append({"source": s, "blocks": blocks})

    return {"sources": d}


@app.delete("/source/{name}")
async def delete_source(name: str):
    collection = index_store.open_index(INDEX_PATH)
    deleted = index_store.delete_source(collection, name)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="来源不存在")

    return {"deleted": deleted}


@app.post("/query", dependencies=[Depends(rate_limit)])
async def query(req: QueryRequest):
    if req.question.strip() == "":
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 索引为空（例如被清理过）时先重建，再走查询；重建失败如实报 500 而不是 404。
    try:
        index_store.ensure_index(INDEX_PATH, config.DATA_DIR)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    collection = index_store.open_index(INDEX_PATH)

    try:
        hits = query_lab.query_index(
            collection, req.question, req.k, max_distance=config.MAX_DISTANCE
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    index_hits: list[tuple[int, str, str]] = [
        (index, source, content)
        for index, (source, content) in enumerate(hits, start=1)
    ]

    context = qa.build_context(index_hits)

    try:
        resp = qa.client.chat.completions.create(
            model=qa.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你只能依据材料回答，缺信息就拒答，引用编号来自材料。",
                },
                {
                    "role": "user",
                    "content": f"参考材料：\n{context}\n\n问题：{req.question}",
                },
            ],
        )
    except AuthenticationError:
        logger.exception("上游鉴权失败")
        raise HTTPException(status_code=500, detail="上游Key失效, 请联系管理员")
    except APITimeoutError:
        logger.exception("上游请求超时")
        raise HTTPException(status_code=503, detail="请求超时, 请稍后")
    except APIConnectionError:
        logger.exception("上游连接失败")
        raise HTTPException(status_code=503, detail="API连接失败")
    except APIStatusError as e:
        if e.status_code == 402:
            logger.exception("上游余额不足")
            raise HTTPException(status_code=503, detail="上游余额不足, 请联系管理员")
        elif e.status_code == 429:
            logger.exception("上游请求过于频繁")
            raise HTTPException(status_code=503, detail="请求太频繁，请重试")
        else:
            logger.exception("上游返回未归类状态 %d", e.status_code)
            raise HTTPException(status_code=500, detail="上游未知错误, 请联系管理员")

    reply = resp.choices[0].message.content
    if not reply:
        raise HTTPException(status_code=502, detail="模型回复为空")
    u = resp.usage

    if not u:
        raise HTTPException(status_code=502, detail="无usage返回")
    query_lab.tokens_calculate(req.question, u.prompt_tokens, u.completion_tokens)

    logger.info("查询成功，命中了 %d 条片段", len(hits))
    return {"answer": reply, "sources": hits}


app.mount(
    "/",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="web",
)
