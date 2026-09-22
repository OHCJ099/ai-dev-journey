from llm import append_reply, ask

SYSTEM_PROMPT = "你是一个简洁的中文助手，回答不超过两句话。"


def main() -> None:
    # ① 开场就一条 system：本次会话的角色设定，之后每一轮都连它一起发出去
    history: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # ② 主循环：一行 = 一轮对话
    while True:
        try:
            line = input("你 > ").strip()  # 管道喂完 / 窗口关了：没人再说话了，正常退出
        except EOFError:
            return

        # TODO(1) 只敲了回车（line 是空字符串）时，你该干什么？想好了再写。
        #         提示：继续发一条空消息给 API 是在浪费 token。
        if not line:
            print("请勿输入空字符串！")
            continue

        # TODO(2) 把这一行用户输入接进 history —— 用哪个 role？
        #         写完对照 llm.py 里的 append_reply：两头的 role 不能撞。
        history.append({"role": "user", "content": line})

        print("AI > ", end="")  # end="" 表示先别换行，等回答接在同一行
        reply, tokens = ask(history)  # 把「全部历史」发出去

        # TODO(3) 把 reply 接进 history（调 append_reply）——
        #         顺序想一下：应该在 ask 之前还是之后？为什么？
        append_reply(history, reply)

        print(reply)
        print(f"[本轮 {tokens} tokens]")  # 不累计，只是让你看见它随轮数变大


if __name__ == "__main__":
    main()
