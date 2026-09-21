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
    raise SystemExit("提示：没找到 key")

client = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT)

question = "你是谁？"

try:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个只会用文言文回答的助手，回答不超过 20 字"},
            {"role": "user", "content": question},
        ],
        extra_body={"thinking": {"type": "disabled"}},   # 关掉思考模式，省 token
    )
except AuthenticationError:
    print("key 不对，请检查 key 是否正确")
except APITimeoutError:
    print("API 请求超时")
except APIConnectionError:
    print("API 连接失败")
except APIStatusError as e:
    if e.status_code == 402:
        print("API 余额不足")
    elif e.status_code == 429:
        print("请求太频繁，请重试")
    else:
        print(f"接口报错(HTTP {e.status_code}):{e.message}")
else:
    print(resp.choices[0].message.content)
    print()
    u = resp.usage
    if u is not None:
        cost = u.prompt_tokens * 0.000002 + u.completion_tokens * 0.000008
        print(f"prompt_tokens:     {u.prompt_tokens}")
        print(f"completion_tokens: {u.completion_tokens}")
        print(f"total_tokens:      {u.total_tokens}")
        print(f"本次费用约 {cost:.6f} 元")