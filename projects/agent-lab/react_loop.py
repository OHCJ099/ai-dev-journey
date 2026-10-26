import json
import os
from typing import cast

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolUnionParam
from tools_demo import TOOLS, TOOLS_BY_NAME

load_dotenv()
# 模型服务地址、密钥、模型名都从 .env 读，换供应商只改 .env。
client = OpenAI(
    base_url=os.getenv("DEEPSEEK_BASE_URL") or "http://127.0.0.1:8787/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
MODEL = os.getenv("DEEPSEEK_MODEL") or "deepseek-v4.1-flash-cn"

MAX_STEPS = 8
MAX_RETRIES = 3


def main() -> None:
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": "12×8 再除以 4",
        }
    ]
    fail_counts: dict[str, int] = {}
    step = 0
    done = False

    while step < MAX_STEPS and not done:
        step += 1
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=cast(list[ChatCompletionToolUnionParam], TOOLS),
        )
        msg = resp.choices[0].message
        reason = resp.choices[0].finish_reason
        print(f"[step {step}] finish_reason={reason}")
        print(
            "  Thought:",
            msg.content or getattr(msg, "reasoning_content", None) or "(无)",
        )

        if reason == "stop":
            print("最终答案:", msg.content)
            done = True
            break

        messages.append(
            cast(ChatCompletionMessageParam, msg.model_dump(exclude_none=True))
        )

        for tc in msg.tool_calls or []:
            if tc.type != "function":
                continue
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
                print(f"  Action: {name}({args})")

                content = ""

                # ─── 空位 A：查表取函数，try 里执行，except 里接住 ───
                tool_use = TOOLS_BY_NAME.get(name)
                if tool_use is None:
                    raise ValueError(f"不存在工具[{name}]")

                result = tool_use.invoke(args)
                content = str(result)

                success = True

            except Exception as e:  # noqa: BLE001 —— 故意兜全部异常，转成 observation 喂回模型
                content = f"ERROR {type(e).__name__}: {e}"
                success = False
                print(f"  Action: {name}(失败，见 Observation)")

            # ─── 空位 B：append 一条 tool 消息，content 就是上面那个 content ───
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": content})

            # ─── 空位 C：更新 fail_counts，某个工具连续失败到 MAX_RETRIES 就 done = True ───
            if success is True:
                fail_counts[name] = 0
            else:
                fail_counts[name] = fail_counts.get(name, 0) + 1

                if fail_counts[name] >= MAX_RETRIES:
                    print(f"⚠️ 工具 {name} 连续失败 {MAX_RETRIES} 次，终止任务。")
                    done = True
                    break

            print(f"  Observation: {content}")

    if not done:
        print(f"步数用尽（{MAX_STEPS} 步），未得到最终答案")


if __name__ == "__main__":
    main()
