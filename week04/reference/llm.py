"""llm.py —— 只负责和大模型说话：发 history 过去、把回答拿回来。这里不出现 input() / print()。

参考实现（答案）。先自己写，卡住 25 分钟以上再看对应片段。
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
ENV_FILE = Path(__file__).parent.parent.parent / ".env"  # 往三级 = 仓库根

load_dotenv(ENV_FILE)
key = os.getenv("TOKENRHYTHM_API_KEY")
if not key:
    raise SystemExit("没找到 TOKENRHYTHM_API_KEY，请检查 .env")

client = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT)


def ask(history: list[dict[str, str]]) -> tuple[str, int]:
    """把 history 整个发出去；返回 (模型这次说的话, 本次用了多少 total_tokens)。"""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=history,  # type: ignore[arg-type]
            extra_body={"thinking": {"type": "disabled"}},
        )
    except AuthenticationError:
        return "key 不对，请检查 key 是否正确", 0
    except APITimeoutError:
        return "API 请求超时", 0
    except APIConnectionError:
        return "API 连接失败", 0
    except APIStatusError as e:
        if e.status_code == 402:
            return "API 余额不足", 0
        if e.status_code == 429:
            return "请求太频繁，请重试", 0
        return f"接口报错(HTTP {e.status_code}):{e.message}", 0
    else:
        answer = resp.choices[0].message.content or ""
        usage = resp.usage
        if usage is None:
            return answer, 0
        return answer, usage.total_tokens


def append_reply(history: list[dict[str, str]], reply: str) -> None:
    """把模型这次的回答接进 history —— 角色是 assistant。"""
    history.append({"role": "assistant", "content": reply})
