# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)


def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为 0")
    return a / b


def multiply(a, b):
    return a * b


def count_chars(text):
    return len(text)


def get_weather(city):
    return f"{city}, 晴, 25℃"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "计算两个数字相除",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "计算两个数字相乘",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_chars",
            "description": "计算文本长度",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要计算长度的文本"}
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取城市天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
]
messages_list = [
    [
        {
            "role": "user",
            "content": "12 乘 8 等于多少，'今天天气不错' 这句话有几个字，北京今天天气怎么样",
        }
    ],
    [{"role": "user", "content": "你是什么模型？"}],
]

TOOLS_BY_NAME = {
    "multiply": multiply,
    "count_chars": count_chars,
    "get_weather": get_weather,
    "divide": divide,
}


if __name__ == "__main__":
    for messages in messages_list:
        r1 = client.chat.completions.create(
            model="deepseek-flash", messages=messages, tools=TOOLS
        )

        msg = r1.choices[0].message

        if r1.choices[0].finish_reason == "stop":
            print("第1轮就结束了，无需调用工具。答案:\n", msg.content)
            print("=========================================")
            continue

        messages.append(msg.model_dump(exclude_none=True))
        print(json.dumps(messages, ensure_ascii=False, indent=2))
        print("第1轮 finish_reason =", r1.choices[0].finish_reason)

        for tc in msg.tool_calls or []:
            args = json.loads(tc.function.arguments)

            tool_use = TOOLS_BY_NAME.get(tc.function.name)
            if tool_use is not None:
                result = tool_use(**args)

            else:
                result = f"未知工具: {tc.function.name}"

            print("执行工具", tc.function.name, args, "→", result)
            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": str(result)}
            )

        r2 = client.chat.completions.create(
            model="deepseek-flash", messages=messages, tools=TOOLS
        )

        print("第2轮 finish_reason =", r2.choices[0].finish_reason)
        print("答案:", r2.choices[0].message.content)

        print("=========================================")
