import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
)
from pydantic import BaseModel, Field

app = FastAPI()
app.mount("/static", StaticFiles(directory="week07/chat_web/static"), name="static")

BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-flash"
TIMEOUT = 60.0
ENV_FILE = Path(__file__).parent.parent / ".env"

load_dotenv(ENV_FILE)
key = os.getenv("DEEPSEEK_API_KEY")
if not key:
    raise SystemExit("没找到 DEEPSEEK_API_KEY，请检查 .env")

client = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT)


class ChatRequest(BaseModel):  # ① 继承 BaseModel
    message: str  # ② 字段名 = JSON 的 key
    system: str = "你是一个有帮助的助手"  # ③ 带默认值 = 可以不传
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)  # ④ Field 加约束：0~2


class ChatStreamRequest(BaseModel):
    messages: list[dict[str, str]] = Field(min_length=1)


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": req.system},
                {"role": "user", "content": req.message},
            ],
            extra_body={"thinking": {"type": "disabled"}},
            stream=False,
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
        raise HTTPException(status_code=502, detail="上游收到无效响应")
    return {"reply": reply}


@app.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest):

    def gen():
        stream = client.chat.completions.create(
            model=MODEL,
            messages=req.messages,  # type: ignore[arg-type]  # 变量形式，pyright 认不出每条 role（W4 同款）
            extra_body={"thinking": {"type": "disabled"}},
            stream=True,
        )

        for chunk in stream:
            if not chunk.choices:
                continue
            else:
                piece = chunk.choices[0].delta.content
                if piece:
                    yield f"data: {piece}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
