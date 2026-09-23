chat_cli · 多轮对话命令行

运行：`uv run python week04/chat_cli/main.py` 自定义角色：`uv run python week04/chat_cli/main.py --system "<角色描述>"`

命令：

- `/clear` （清空对话，保留角色）
- `/system <提示词>` （<一句话>）
- `/save` （<一句话>）
- `/exit` （<一句话>）

功能：多轮上下文（<发多少、封顶多少>）、流式输出、token 统计、日志写 `chat.log`

技术栈：`openai` SDK 调中转端点 `tokenrhythm.studio/v1`，模型 `deepseek-flash`；key 从 `.env` 读

踩的坑：

1. 现象：history = history[0] + history[-keep:]:错误，history = [history[0]] + history[-keep:]:正确
   原因：因为字典无法与列表直接拼接，对传参数据类型不熟悉
   修法：[history[0]]加上[]后即可修复
2. 现象：asctimeds参数名打错，会导致无日志，无报错
   原因：`format` 里的 `%(xxx)s` 必须是记录对象上存在的字段名
   修法：将其修正为正确参数名asctime，逐条对齐为准
3. 会话裁切时机：第 11 轮发出时是 22 条（21 条已有 + 1 条新 user），收到回复变成 23 条 → 裁到 21 条；所以发出时刻永远封顶 22 条，为什么不放在 `ask` 之前：那时历史是奇数条，`[-20:]` 会切掉最老的 user、留下配对的 assistant，历史变成以 assistant 开头。

坑那三条用你刚才自己校准好的表述（别照抄我的原话，写成你自己能讲给面试官听的版本）。