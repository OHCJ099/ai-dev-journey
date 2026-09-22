import json
from pathlib import Path

from llm import append_reply, ask

SYSTEM_PROMPT = "你是一个简洁的中文助手，回答不超过两句话"


def main() -> None:
    # ① 开场就一条 system：本次会话的角色设定，之后每一轮都连它一起发出去
    history: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    total_tokens = 0  # 从开场到现在的累计用量（每轮 +1 次）

    # ② 主循环：一行 = 一轮对话
    while True:
        try:
            line = input("你 > ").strip()  # 管道喂完 / 窗口关了：没人再说话了，正常退出
        except EOFError:
            return

        if not line:
            print("请勿输入空字符串！")
            continue

        parts = line.split(maxsplit=1)
        if parts[0].startswith("/clear"):
            if line != "/clear":
                print("格式是: /clear")
                continue
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("清除上下文")
            continue

        if parts[0].startswith("/save"):
            if line != "/save":
                print("格式是: /save")
                continue
            save_file = Path(__file__).parent / "session.json"
            save_file.write_text(
                json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"已保存到 {save_file.name}")
            print(f"本次会话共 {total_tokens} tokens")
            continue

        if parts[0].startswith("/system"):
            if len(parts) != 2:
                print("正确的格式为: /system <提示词>")
                continue
            history[0]["content"] = parts[1]
            print("提示词设置成功")
            continue

        if parts[0].startswith("/exit"):
            print(f"本次会话共 {total_tokens} tokens")
            print("再见")
            break

        if line.startswith("/"):
            print("未知命令，可用：/clear /system /save /exit")
            continue

        history.append({"role": "user", "content": line})
        print("AI > ", end="")  # end="" 表示先别换行，等回答接在同一行
        reply, tokens = ask(history)  # 把「全部历史」发出去
        append_reply(history, reply)
        total_tokens += tokens
        print(f"[本轮 {tokens} | 累计 {total_tokens}]")


if __name__ == "__main__":
    main()
