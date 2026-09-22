"""llm.py —— 只负责和大模型说话：发 history 过去、把回答逐块吐出来。不出现 input()。

v1 妥协：所有给人看的输出（逐字回答 + 错误提示）暂放在这里，W6 改成 SSE 时挪到接口层。
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
)

BASE_URL = "https://tokenrhythm.studio/v1"
MODEL = "deepseek-flash"
TIMEOUT = 60.0
ENV_FILE = Path(__file__).parent.parent.parent / ".env"  # 往上三级 = 仓库根

load_dotenv(ENV_FILE)
key = os.getenv("TOKENRHYTHM_API_KEY")
if not key:
    raise SystemExit("没找到 TOKENRHYTHM_API_KEY，请检查 .env")

client = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT)


def ask(history: list[dict[str, str]]) -> tuple[str, int]:
    """把 history 整个发出去；返回 (模型这次说的话, 本次用了多少 total_tokens)。"""
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=history,  # type: ignore[arg-type]  # SDK 要严格形状，我们给宽泛字典，运行时没问题
            extra_body={"thinking": {"type": "disabled"}},
            stream=True,
        )
    except AuthenticationError:
        msg = "key 不对，请检查 key 是否正确"
        print(msg)
        return msg, 0
    except APITimeoutError:
        msg = "API 请求超时"
        print(msg)
        return msg, 0
    except APIConnectionError:
        msg = "API 连接失败"
        print(msg)
        return msg, 0
    except APIStatusError as e:
        if e.status_code == 402:
            msg = "API 余额不足"
        elif e.status_code == 429:
            msg = "请求太频繁，请重试"
        else:
            msg = f"接口报错(HTTP {e.status_code}):{e.message}"
        print(msg)
        return msg, 0
    else:
        temp = ""
        usage = 0
        for chunk in stream:
            if chunk.usage is not None:
                usage = chunk.usage.total_tokens
            if not chunk.choices:
                continue
            piece = chunk.choices[0].delta.content
            if piece:
                print(piece, end="", flush=True)
                temp += piece

        print()
        return temp, usage


def append_reply(history: list[dict[str, str]], reply: str) -> None:
    history.append({"role": "assistant", "content": reply})
