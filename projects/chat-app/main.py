# 聊天后端：接收浏览器消息，调用模型并返回普通或流式回复。
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

# 创建接口服务，并让浏览器能访问 static 目录中的聊天页面。
app = FastAPI()
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)

# 模型服务地址、模型名和请求超时时间。
BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-flash"
TIMEOUT = 60.0
ENV_FILE = Path(__file__).parent.parent.parent / ".env"

# 从仓库根目录的 .env 读取密钥；缺少密钥时停止启动。
load_dotenv(ENV_FILE)
key = os.getenv("DEEPSEEK_API_KEY")
if not key:
    raise SystemExit("没找到 DEEPSEEK_API_KEY，请检查 .env")

# 使用兼容 OpenAI 的客户端连接 DeepSeek。
client = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT)


# 普通聊天的请求格式：Pydantic 会检查字段类型和取值范围。
class ChatRequest(BaseModel):  # ① 继承 BaseModel
    message: str  # ② 字段名 = JSON 的 key
    system: str = "你是一个有帮助的助手"  # ③ 带默认值 = 可以不传
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)  # ④ Field 加约束：0~2


# 流式聊天接收整段对话历史，列表至少要有一条消息。
class ChatStreamRequest(BaseModel):
    messages: list[dict[str, str]] = Field(min_length=1)


# 普通接口：等模型生成完整回答后，再一次性返回 JSON。
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            # system 指定助手要求，user 提供本次问题。
            messages=[
                {"role": "system", "content": req.system},
                {"role": "user", "content": req.message},
            ],
            extra_body={"thinking": {"type": "disabled"}},
            stream=False,
        )
    # 将上游调用错误转换成前端能理解的 HTTP 错误。
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

    # choices 是候选回答列表，这里取第一条回答的正文。
    reply = resp.choices[0].message.content
    if not reply:
        raise HTTPException(status_code=502, detail="上游收到无效响应")
    return {"reply": reply}


# 流式接口：用 SSE（服务器推送事件）逐段发送回答。
@app.post("/chat/stream")
async def chat_stream(req: ChatStreamRequest):
    # 生成器每次 yield 一段数据，浏览器就能逐步显示回复。
    def gen():
        # 先初始化，确保请求失败后也能安全判断是否有用量信息。
        token = None
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=req.messages,  # type: ignore[arg-type]  # 此处的字典类型比 SDK 要求宽，忽略该参数的类型提示
                extra_body={"thinking": {"type": "disabled"}},
                stream=True,
            )

            for chunk in stream:
                # 用量信息用于统计 tokens，不作为回复正文显示。
                if chunk.usage is not None:
                    token = chunk.usage.total_tokens
                    continue

                # 有些片段没有回答内容，直接跳过。
                if not chunk.choices:
                    continue
                else:
                    piece = chunk.choices[0].delta.content
                    if piece:
                        # data: 是 SSE 数据前缀，两个换行表示一条事件结束。
                        yield f"data: {piece}\n\n"

        except Exception:  # noqa: BLE001 —— 流已开始，异常也用事件通知前端
            yield "data: [错误] 上游异常，请重试\n\n"

        # 最后发送可用的用量信息和结束标记，供前端识别。
        if token is not None:
            yield f"data: [USAGE_TOKEN]{token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
