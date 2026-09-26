# 浏览器聊天页 —— 单 HTML + SSE 流式

**这是什么**：一个能在浏览器里聊天的页面（`week07/chat_web/static/index.html`）。后端推流式回答，页面上的字一个个蹦出来；对话历史存在浏览器里，支持连续多轮。

**怎么跑起来**

```
uv run uvicorn week07.main:app --reload
```

浏览器打开 `http://127.0.0.1:8000/static/index.html`（`/static` 是 `main.py` 里 `app.mount` 挂的静态目录）。

命令行验证流式接口（Windows 坑：必须写 `curl.exe`，`curl` 是 PowerShell 别名；`-N` 关缓冲，不写看不出流式效果）：

```
curl.exe -N -X POST http://127.0.0.1:8000/chat/stream -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"数到五"}]}'
```

**流式是怎么串起来的（一条链）**

用户点发送 → `fetch("/chat/stream")` 把整个 history 发过去 → 后端 `gen()` 调 SDK（`stream=True`）拿到分片迭代器 → 每片文本 `yield "data: <文本>\n\n"`（SSE 格式）→ `StreamingResponse` 一路推给浏览器 → 前端 `getReader()` 一段段读、`TextDecoder`（带 `{stream:true}`）翻成中文 → 按空行拆帧、剥掉 `data: ` 前缀 → 拼进气泡。`data: [DONE]` 是收尾哨兵（不是 SSE 标准，OpenAI 的约定）。

**踩的坑**

1. 现象：浏览器打开页面是 `{"detail":"Not Found"}`（404）
   原因：后端没有挂载静态目录 —— HTML 躺在磁盘上，服务不知道要发它
   修法：`app.mount("/static", StaticFiles(directory="week07/chat_web/static"), name="static")`

2. 现象：curl 输出里每个字后面都跟一条 `data: None`
   原因：`yield f"data: {None}\n\n"` 写在了 `if/else` 外面、`for` 里面 —— 每个分片都执行一次，而且 `{None}` 是字面量
   修法：删掉那行；判空判列表本身（`if not chunk.choices:`，列表空时 `[0]` 会 `IndexError`）

3. 现象：页面能发消息，但永远收不到回复
   原因：前端发 `{ message: text }`、后端流式接口收 `messages` 数组 —— 键名对不上，请求 422
   修法：前端 `body: JSON.stringify({ messages: history })`；后端新模型 `ChatStreamRequest`（`Field(min_length=1)` 拦空数组 —— 空数组会到上游报 400）

4. 现象：后端关掉后发消息，页面完全没反应，刷新后消息没了
   原因：`fetch` 抛的错没人接；`replyText` 没收到回复也是空的
   修法：`try/catch/finally` 包住整段 —— catch 里 `addBubble` 留提示，`finally` 里解锁按钮；`history.push(assistant)` 挪进 try（只在真收到回复时存）
