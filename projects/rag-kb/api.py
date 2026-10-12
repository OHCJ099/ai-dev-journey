from fastapi import FastAPI, File, UploadFile

app = FastAPI()


# 这里只演示接收文件，暂不保存、不入库。
@app.post("/upload")
async def upload(file: UploadFile = File(...)):  # noqa: B008 -- FastAPI 上传字段声明，不是可变默认容器。
    content = await file.read()
    return {"filename": file.filename, "bytes": len(content)}
