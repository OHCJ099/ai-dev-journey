"""chat_cli v0.1 参考实现（答案key）—— 先自己写，卡住 25 分钟以上再看对应片段。

本文件是「合并成单文件」的版本，方便你对照结构与逻辑；
真正提交时按 W3 任务拆成 llm.py / session.py / main.py，体现分层。
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import APIError, APIConnectionError, APIStatusError, OpenAI

# ---------- 配置 ----------
BASE_URL = os.getenv("BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("MODEL", "deepseek-flash")   # 通义改 https://dashscope.aliyuncs.com/compatible-mode/v1 + qwen-plus
DEFAULT_SYSTEM = "你是一个严谨的中文技术助手，回答简洁准确。"
SESSIONS_DIR = Path("sessions")


class LLMClient:
    """只负责和大模型说话。这里不出现 input() / print()。"""

    def __init__(self, api_key: str, base_url: str = BASE_URL, model: str = MODEL) -> None:
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=60.0)

    def chat(self, messages: list[dict[str, str]]) -> tuple[str, dict[str, int]]:
        """流式调用，边收边打印；返回 (完整回复, 本次 token 用量)。"""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,   # type: ignore[arg-type]
                stream=True,
                temperature=1.0,
            )
        except APIConnectionError as e:
            return f"[网络错误] 连接失败：{e}", {}
        except APIStatusError as e:
            hint = {401: "API Key 无效或已过期", 402: "余额不足，请充值", 429: "触发限速，稍后再试"}.get(
                e.status_code, "服务端返回错误"
            )
            return f"[调用失败 {e.status_code}] {hint}：{e}", {}
        except APIError as e:
            return f"[调用失败] {e}", {}

        parts: list[str] = []
        usage: dict[str, int] = {}
        try:
            for chunk in stream:
                if chunk.usage:                       # 只有开 stream_options 时才有，但兼容性判断无害
                    usage = {
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens,
                    }
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:                             # 关键：content 可能是 None
                    parts.append(delta)
                    sys.stdout.write(delta)
                    sys.stdout.flush()
        except KeyboardInterrupt:
            parts.append("\n[已中断]")
        sys.stdout.write("\n")
        return "".join(parts), usage


class Session:
    """只管上下文与 token 账本。"""

    def __init__(self, system_prompt: str = DEFAULT_SYSTEM) -> None:
        self.system_prompt = system_prompt
        self.messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        self.total_tokens = 0
        self.turns = 0

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})
        self.turns += 1

    def clear(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def set_system(self, text: str) -> None:
        self.system_prompt = text
        self.messages[0] = {"role": "system", "content": text}

    def save(self, sessions_dir: Path = SESSIONS_DIR) -> Path:
        sessions_dir.mkdir(parents=True, exist_ok=True)
        path = sessions_dir / f"{datetime.now():%Y-%m-%d-%H%M%S}.json"
        path.write_text(
            json.dumps(
                {"system": self.system_prompt, "messages": self.messages, "total_tokens": self.total_tokens},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return path


HELP = """指令：
  /clear              清空上下文
  /system <提示词>     切换角色
  /save               保存当前会话到 sessions/
  /help               显示帮助
  /exit               退出
"""


def main() -> None:
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("缺少 DEEPSEEK_API_KEY，请在 .env 里配置（参考 .env.example）")
        sys.exit(1)

    llm = LLMClient(api_key=api_key, model=os.getenv("MODEL", MODEL))
    session = Session()
    print(f"chat_cli v0.1 | model={llm.model} | /help 查看指令\n")

    while True:
        try:
            user_input = input("你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见")
            break
        if not user_input:
            continue

        if user_input.startswith("/"):
            cmd, _, arg = user_input.partition(" ")
            if cmd in ("/exit", "/quit"):
                print(f"共 {session.turns} 轮，累计 {session.total_tokens} tokens")
                break
            if cmd == "/clear":
                session.clear()
                print("上下文已清空")
            elif cmd == "/system":
                session.set_system(arg.strip() or DEFAULT_SYSTEM)
                print(f"角色已切换：{session.system_prompt}")
            elif cmd == "/save":
                print(f"已保存：{session.save()}")
            else:
                print(HELP)
            continue

        session.add_user(user_input)
        print("AI > ", end="")
        reply, usage = llm.chat(session.messages)
        session.add_assistant(reply)
        if usage:
            session.total_tokens += usage.get("total_tokens", 0)
            print(f"[本次 {usage.get('total_tokens', 0)} tokens | 累计 {session.total_tokens}]")


if __name__ == "__main__":
    main()
