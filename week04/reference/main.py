"""main.py —— 只管终端交互：读一行、写进 history、要回答、打印。

参考实现（答案）。先自己写，卡住 25 分钟以上再看对应片段。
"""

from llm import append_reply, ask

SYSTEM_PROMPT = "你是一个简洁的中文助手，回答不超过两句话。"


def main() -> None:
    history: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            line = input("你 > ").strip()
        except EOFError:
            return

        if not line:  # 只敲回车：没有内容可发，别浪费 token
            continue

        history.append({"role": "user", "content": line})

        print("AI > ", end="")
        reply, tokens = ask(history)

        append_reply(history, reply)  # 必须在 ask 之后：reply 这时才存在

        print(reply)
        print(f"[本轮 {tokens} tokens]")


if __name__ == "__main__":
    main()
