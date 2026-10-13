import io
from pathlib import Path

import index_store
import ingest
import loader
import pypdf.errors
import qa
import query_lab
from api_models import QueryRequest
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
)
from pypdf import PdfReader

app = FastAPI()

UPLOAD_PATH = Path("D:/Hermes/cache/scratch/w14/uploads")
INDEX_PATH = Path("D:/Hermes/cache/scratch/w14/index_offline")
TEMP_PATH = Path("D:/Hermes/cache/scratch/w14/Temps")


# 接收上传文件，保存后调用已有入库函数。
@app.post("/upload")
async def upload(file: UploadFile = File(...)):  # noqa: B008 -- FastAPI 上传字段声明，不是可变默认容器。
    content = await file.read()
    if file.filename is None or file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="文件名不能为空")
    file_path = UPLOAD_PATH / Path(file.filename).name

    suffix = file_path.suffix.lower()
    if suffix == ".md":
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as e:
            raise HTTPException(status_code=400, detail=f"文件编码无法识别：{e}")
    elif suffix == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except pypdf.errors.PyPdfError as e:
            raise HTTPException(status_code=400, detail=f"文件无法解析[{e}]")
    else:
        raise HTTPException(status_code=400, detail="只支持.md .pdf")

    cleaned = loader.clean_text(text)
    if len(cleaned) == 0:
        raise HTTPException(status_code=400, detail="文件不能为空")

    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

    file_path.write_bytes(content)

    try:
        count = ingest.ingest_file(file_path, INDEX_PATH, True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"source": file_path.name, "blocks": count}


@app.get("/sources")
async def get_collectino():
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
    collectino = index_store.open_index(INDEX_PATH)
    deleted = index_store.delete_source(collectino, name)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="来源不存在")

    return {"deleted": deleted}


@app.post("/query")
async def query(req: QueryRequest):
    collection = index_store.open_index(INDEX_PATH)
    if req.question.strip() == "":
        raise HTTPException(status_code=400, detail="问题不能为空")
    if collection.count() == 0:
        raise HTTPException(status_code=404, detail="索引无块")

    try:
        hits = query_lab.query_index(collection, req.question, req.k)
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
        raise HTTPException(status_code=500, detail="上游Key失效, 请联系管理员")
    except APITimeoutError:
        raise HTTPException(status_code=503, detail="请求超时, 请稍后")
    except APIConnectionError:
        raise HTTPException(status_code=503, detail="API连接失败")
    except APIStatusError as e:
        if e.status_code == 402:
            raise HTTPException(status_code=503, detail="上游余额不足, 请联系管理员")
        elif e.status_code == 429:
            raise HTTPException(status_code=503, detail="请求太频繁，请重试")
        else:
            raise HTTPException(status_code=500, detail="上游未知错误, 请联系管理员")

    reply = resp.choices[0].message.content
    if not reply:
        raise HTTPException(status_code=502, detail="模型回复为空")
    return {"answer": reply, "sources": hits}


app.mount(
    "/",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="web",
)
