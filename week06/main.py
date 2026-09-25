import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
)
from pydantic import BaseModel, Field

app = FastAPI()

BASE_URL = "https://tokenrhythm.studio/v1"
MODEL = "deepseek-flash"
TIMEOUT = 60.0
ENV_FILE = Path(__file__).parent.parent / ".env"

load_dotenv(ENV_FILE)
key = os.getenv("TOKENRHYTHM_API_KEY")
if not key:
    raise SystemExit("没找到 TOKENRHYTHM_API_KEY，请检查 .env")

client = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT)


class ChatRequest(BaseModel):  # ① 继承 BaseModel
    message: str  # ② 字段名 = JSON 的 key
    system: str = "你是一个有帮助的助手"  # ③ 带默认值 = 可以不传
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)  # ④ Field 加约束：0~2


@app.get("/")
async def root():
    return {"message": "hello"}


@app.post("/echo")
async def echo(text: str, times: int):
    return {"you_said": text, "times": times}


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": req.system},
                {"role": "user", "content": req.message},
            ],  # type: ignore[arg-type]  # SDK 要严格形状，我们给宽泛字典，运行时没问题
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
            raise HTTPException(
                status_code=500, detail="服务端Key余额不足, 请联系管理员"
            )

    reply = resp.choices[0].message.content
    if not reply:
        raise HTTPException(status_code=502, detail="上游收到无效响应")
    return {"reply": reply}
