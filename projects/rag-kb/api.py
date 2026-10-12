from pathlib import Path

import ingest
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI()

UPLOAD_PATH = Path("D:/Hermes/cache/scratch/w14/uploads")
INDEX_PATH = Path("D:/Hermes/cache/scratch/w14/index_offline")


# 接收上传文件，保存后调用已有入库函数。
@app.post("/upload")
async def upload(file: UploadFile = File(...)):  # noqa: B008 -- FastAPI 上传字段声明，不是可变默认容器。
    content = await file.read()
    if file.filename is None or file.filename.strip() == "":
        raise HTTPException(status_code=400, detail="文件名不能为空")

    file_path = UPLOAD_PATH / Path(file.filename).name
    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)

    try:
        count = ingest.ingest_file(file_path, INDEX_PATH)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"source": file_path.name, "blocks": count}
