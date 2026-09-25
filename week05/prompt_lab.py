import json
import os

from dotenv import load_dotenv
from openai import OpenAI

# 配置

BASE_URL = "https://tokenrhythm.studio/v1"
MODEL = "deepseek-flash"
TIMEOUT = 60.0

load_dotenv()
key = os.getenv("TOKENRHYTHM_API_KEY")
if not key:
    raise SystemExit("提示：没找到 key")

client = OpenAI(base_url=BASE_URL, api_key=key, timeout=TIMEOUT)


# 模型响应
def run(system, user, temperature=1.0) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        extra_body={"thinking": {"type": "disabled"}},
        stream=False,
    )
    text = resp.choices[0].message.content
    if not text:
        text = ""
    return text


# SYSTEM PROMPT对照表
CASES = [
    {"组": "A", "system": None, "user": "python: a=1;b='1';a+b为什么报错？"},
    {
        "组": "B",
        "system": "你是一个严格的代码审查员，只指出问题，不给安慰",
        "user": "python: a=1;b='1';a+b为什么报错？",
    },
    {
        "组": "C",
        "system": "你是一个鼓励型编程导师，先肯定再提建议",
        "user": "python: a=1;b='1';a+b为什么报错？",
    },
    {
        "组": "少样本-0",
        "system": "请你以以下的格式输出：[时间]: [地点]: [受害者]: [始作俑者]: [事件]:",
        "user": "请从以下对话中提取关键信息：小王今天去学校的路途中买了个煎饼果子，吃到一半时发现煎饼果子中间的肉是酸的！他生气极了，回去和老板理论了一番",
    },
    {
        "组": "少样本-1",
        "system": "请你以以下的格式输出：[时间]: [地点]: [受害者]: [始作俑者]: [事件]:，例如--[时间]: 今天中午 [地点]: 小美家里 [受害者]:小王 [始作俑者]:小美 [事件: 小美打了小王一巴掌]",
        "user": "请从以下对话中提取关键信息：小王今早去学校的路途中买了个煎饼果子，吃到一半时发现煎饼果子中间的肉是酸的！他生气极了，回去和老板理论了一番",
    },
    {
        "组": "少样本-2",
        "system": "请你以以下的格式输出：[时间]: [地点]: [受害者]: [始作俑者]: [事件]:，例如--[时间]: 今天中午 [地点]: 小美家里 [受害者]:小王 [始作俑者]:小美 [事件: 小美打了小王一巴掌] 案例2:[时间]: 今天晚上 [地点]: 沙滩边 [受害者]:小赵 [始作俑者]:路边的狗 [事件: 小赵踩到狗屎了]",
        "user": "请从以下对话中提取关键信息：小王今早去学校的路途中买了个煎饼果子，吃到一半时发现煎饼果子中间的肉是酸的！他生气极了，回去和老板理论了一番",
    },
    {
        "组": "JSON提取",
        "system": "把用户提供的信息整理成 JSON 输出，字段为 <字段A>、<字段B>、<字段C>，只输出 JSON，不要任何多余文字",
        "user": "请从以下对话中提取关键信息：小王今天去学校的路途中买了个煎饼果子，吃到一半时发现煎饼果子中间的肉是酸的！他生气极了，回去和老板理论了一番",
    },
]

print("==============================SYSTEM_PROMPT对照表==============================")

for case in CASES:
    reply = run(case["system"], case["user"])
    print(
        f"组: {case['组']} system摘要: {(case['system'] or '无')[:15]} 回复: {reply[:30]}"
    )

print("==============================TEMPERATURE对照表==============================")

# 温度对照表
ques = "给一家宠物店的狗起个名字"
SYSTEM_PROMPT = "你是宠物取名助手"

for i in [0.2, 1.0, 1.5]:
    print(f"----------温度 {i}----------")
    for j in range(1, 4):
        reply = run(SYSTEM_PROMPT, ques, temperature=i)
        print(f"第 {j} 次, system: {SYSTEM_PROMPT} 回复: {reply[100:130]}")

print("==============================文本解析==============================")

# 文本解析
system_list = [
    "把用户提供的信息整理成 JSON 输出，字段为 <字段A>、<字段B>、<字段C>，只输出 JSON，不要任何多余文字",
    "把用户提供的信息整理",
    "先用自然语言解释精简原话例如：小王在睡觉，再把用户提供的信息整理成 JSON 输出，字段为 <字段A>、<字段B>、<字段C>",
]

user = "请从以下对话中提取关键信息：小王今天去学校的路途中买了个煎饼果子，吃到一半时发现煎饼果子中间的肉是酸的！他生气极了，回去和老板理论了一番"
for system in system_list:
    text = run(system, user)
    try:
        data = json.loads(text)
        print(f"解析成功！文本: {text}")
    except json.JSONDecodeError:
        print(f"解析失败！文本: {text}")
    else:
        try:
            data["字段A"]
        except KeyError:
            print(f"找不到字段A: {data}")
        else:
            print(data["字段A"])
    print("-----------------分割线-----------------")
