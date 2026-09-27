# 浏览器聊天页 —— 单 HTML + SSE 流式

**这是什么**：一个能在浏览器里聊天的页面（`projects/chat-app/static/index.html`）。后端推流式回答，页面上的字一个个蹦出来；对话历史存在浏览器里，支持连续多轮。

**怎么跑起来**（在仓库根执行）：

```
uv sync                                   # 安装依赖
# 仓库根建 .env，写入：DEEPSEEK_API_KEY=<你的key>
uv run uvicorn main:app --app-dir projects/chat-app --reload
# 浏览器打开 http://127.0.0.1:8000/static/index.html

# curl 验证流式接口（-N 关缓冲，不写看不出流式效果）：
curl.exe -N -X POST http://127.0.0.1:8000/chat/stream -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"数到三"}]}'
```

**功能与接口**：

- 功能：多轮对话、流式显示、tokens 累计、重新开始
- 接口：`POST /chat`（非流式）；`POST /chat/stream`（流式，SSE）

**架构：数据怎么流**

1. 用户在聊天框打字发送
2. JS 把拼好的 history 传给后端 /chat/stream 接口
3. 后端 gen() 方法返回流，并包装为 `data: xxx` 的形式推回
4. 前端添加气泡展示聊天记录
5. 流读取器读取二进制 → 解码器解码 → buffer 拼接
6. 一边过滤 `data: ` → 一边拼接、重赋字符串 → 循环刷新流
7. 将完整返回拼入 history
8. 用户再打字发送 → 循环……


**踩的坑**

1. 现象：搬进 `projects/chat-app/` 后，从别的目录启动服务会直接崩：`RuntimeError: Directory 'week07/chat_web/static' does not exist`
   原因：`directory=` 的相对路径是相对**启动命令所在的目录**解析的，不是相对 `main.py` 自己；换个目录启动就找不到
   修法：改用 `Path(__file__).parent` 锚定文件自身位置 —— `app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")`
2. 现象：坏 key 时流被截断 —— 客户端收到 `[错误]` 帧后连接就断，连 `[DONE]` 都收不到；服务端报 `UnboundLocalError: cannot access local variable 'token'`
   原因：`token` 初始化在 `try` 里、读取在 `try` 之后 —— `create()` 抛错时赋值从没执行，读它直接崩；而且崩在 `except` 之外，接不住
   修法：初始化挪到 `try` 之前（`token = None`），发帧前判 `if token is not None:`
3. 现象：累计 tokens 会显示成 `0[USAGE_TOKEN]143[USAGE_TOKEN]35` 这种字符串
   原因：`Number(...)` 的返回值没接住；`+=` 又把整个 `"[USAGE_TOKEN]143"` 当字符串拼了上去
   修法：`totalTokens += Number(piece.slice(13));` —— 把 `Number()` 的返回值接住再累加
