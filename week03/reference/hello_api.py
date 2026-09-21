"""参考实现：week03/hello_api.py —— 第一次调用大模型 API。

卡住 25 分钟以上再看这个文件。
运行：uv run python week03/reference/hello_api.py（在仓库根目录）
"""

import os

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

load_dotenv()
key = os.getenv("TOKENRHYTHM_API_KEY")
if not key:
    raise SystemExit("没找到 TOKENRHYTHM_API_KEY，请检查 .env")

client = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT)

question = "用一句话介绍你自己"

try:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个简洁的助手，回答不超过两句话。"},
            {"role": "user", "content": question},
        ],
        extra_body={"thinking": {"type": "disabled"}},
    )
except AuthenticationError:
    print("认证失败：API key 不对或已失效，请检查 .env 里的 TOKENRHYTHM_API_KEY")
except APITimeoutError:
    print(f"请求超时（超过 {TIMEOUT} 秒）：网络慢或服务繁忙，稍后重试")
except APIConnectionError:
    print("连不上服务器：检查网络，或确认 base_url 没写错")
except APIStatusError as e:
    if e.status_code == 402:
        print("余额不足：去平台充值后再试")
    elif e.status_code == 429:
        print("请求太频繁（限流）：歇几秒再试")
    else:
        print(f"接口报错（HTTP {e.status_code}）：{e.message}")
else:
    print(resp.choices[0].message.content)
    print()
    u = resp.usage
    print(f"prompt_tokens:     {u.prompt_tokens}")
    print(f"completion_tokens: {u.completion_tokens}")
    print(f"total_tokens:      {u.total_tokens}")
