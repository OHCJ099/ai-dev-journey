from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI()

UPLOAD_PATH = Path("D:/Hermes/cache/scratch/w14/uploads")


# 当前只接收并保存文件，暂不入库。
@app.post("/upload")
async def upload(file: UploadFile = File(...)):  # noqa: B008 -- FastAPI 上传字段声明，不是可变默认容器。
    content = await file.read()
    if file.filename is None or file.filename.strip() == "":
        raise HTTPException(400)

    file_path = UPLOAD_PATH / Path(file.filename).name
    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)
    return {"filename": file.filename, "bytes": len(content)}
