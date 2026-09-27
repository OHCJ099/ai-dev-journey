# week07 聊天页 · JS 逐行对照（吃透版）

> **用法**：这是给你**啃**的材料，不是课文。左边开 `index.html`，右边开这份，一行行对。
> **读法**：① §0 总图 30 秒 → ② §1-§2 打底 5 分钟 → ③ §3 逐行表（花大部分时间）→ ④ §4 三个难点 → ⑤ §6 自测。
> **验收**：读完后我随便指一行，你讲出它在干什么。讲不出的**行号**贴给我，我补讲 —— 这就是今天第 0 件的过法。
> **可信度**：本文所有「实测」输出都真跑过（node 探针），不是凭记忆写的。

## §0 总图：一条消息的一生

```
你在输入框打字 → 点「发送」
  → send() 被调用
  → 把你这句存进 history（{role:"user", ...}）
  → fetch 把整个 history 发到后端 /chat/stream
  → 后端流式返回，一段段到浏览器
  → while 循环一段段收：解码 → 拆帧 → 剥前缀 → 拼进气泡
  → 收完：把 AI 回复也存进 history（下一轮要用）
  → finally：按钮解锁
```

页面里所有代码，都在服务这条链。

## §1 页面骨架（第 1-22 行）：每个标签一个名字

| 行 | 代码 | 一句话 |
|---|---|---|
| 2 | `<!DOCTYPE html>` | 告诉浏览器「这是 HTML 文档」（固定写法） |
| 3 | `<html lang="zh">` | 整个页面从这里开始，语言中文 |
| 5-8 | `<meta charset="utf-8">` / `<title>` | 页面「头部」：字符编码、浏览器标签页标题（固定写法） |
| 10-22 | `<body>` | 页面**可见**部分全在这里 |
| 12 | `<h3>…</h3>` | 一行标题 |
| 15 | `<div id="messages" …></div>` | 一块**空区域**，`id="messages"` 是它的名字牌 —— JS 靠这个名字找到它、往里塞消息 |
| 18 | `<input id="input" …>` | 输入框，名字牌 `input` |
| 21 | `<button id="send">发送</button>` | 按钮，名字牌 `send` |
| 23 | `<script>…</script>` | 「页面里所有 JS 都放这里」，从这里开始是 JS |

要点只有一条：**HTML 是结构，`id` 是名字牌，JS 用 `getElementById("名字牌")` 找到元素。**

## §2 四个 JS 小零件（先认脸，§3 里会一直用）

### ① 真假值：`if (!text) return;`
JS 里空字符串 `""` 算「假」。实测：

```
!""     → true      （空 → 假 → ! 取反成 true）
!"abc"  → false
```

所以 `if (!text) return;` = 「输入框是空的就结束」= Python 的 `if not text: return`。

### ② 函数 / async / await
- `function addBubble(text) { … }` = `def add_bubble(text): …`
- `async function send()` = 「这个函数里有要等的操作」；`await fetch(…)` = 停在原地等结果 —— 写法上等价于你 W3 写过的 `await client.post(...)`（异步 httpx）。

### ③ 对象字面量与解构
- `{ role: "user", content: text }` = 一个对象 = **Python 的 dict**：`{"role": "user", "content": text}`
- 解构 `const { done, value } = …` = 按名字掏出字段。实测：

```
const obj = { done: false, value: ... };
const { done, value } = obj;      // done=false，value=...
```

等价 Python：`done = result["done"]; value = result["value"]` —— JS 一行写完。

### ④ 数组
- `const history = [];` = `history = []`
- `history.push(x)` = `.append(x)`
- `history.length` = `len(history)`

## §3 send() 逐行表（第 43-112 行）

### 6.1 读取输入（44-47 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 45 | `const text = inputEl.value.trim();` | 从输入框取值（`.value`），`.trim()` 去首尾空格 —— 同 Python `.strip()` |
| 46 | `if (!text) return;` | 空输入直接结束（见 §2①） |
| 47 | `inputEl.value = "";` | 清空输入框（`元素.value = 新值` 就是写回去） |

### 6.2 记下你说的话（49-51 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 50 | `addBubble("我：" + text);` | 造一条气泡显示出来（`+` 拼字符串） |
| 51 | `history.push({ role: "user", content: text });` | 把这句话**存进历史**（dict 推进 list）—— 下一轮发给后端当上下文 |

### 6.3 准备工作（53-57 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 55 | `let replyText = "";` | 空字符串，**攒 AI 回复**用。`let` = 以后要重新赋值的变量 |
| 57 | `sendBtn.disabled = true` | 禁用按钮（防连点）—— 「按钮变灰」 |

### 6.4 发请求（59-64 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 60 | `const resp = await fetch("/chat/stream", {` | 向后端发请求，**等**响应（`await`） |
| 61 | `method: "POST",` | 用 POST |
| 62 | `headers: { "Content-Type": "application/json" },` | 告诉后端「发的是 JSON」—— 同 curl 的 `-H` |
| 63 | `body: JSON.stringify({ messages: history }),` | JS 对象 → JSON **字符串**再发（HTTP 只传字符串）。`{ messages: history }` = `{"messages": [...历史...]}` |

### 6.5 检查状态码（66-69 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 67 | `if (!resp.ok) {` | `resp.ok` = 状态码是否 2xx；`!` 取反 → **不是 2xx 就进来** |
| 68 | `throw new Error(\`HTTP ${resp.status}\`);` | 主动抛错（`throw` ≈ Python `raise`）→ 跳到 `catch` |

### 6.6 准备读流（71-75 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 72 | `const reader = resp.body.getReader();` | 响应体是**字节流**，拿一个「读取器」—— 给水管装龙头 |
| 73 | `const decoder = new TextDecoder();` | 字节 → 文字的翻译机（§4②） |
| 74 | `const replyEl = addBubble("AI：");` | 先造一条空 AI 气泡，**拿住它的引用**，后面往里填字 |
| 75 | `let buffer = "";` | 暂存「半截数据」的空字符串（§4①） |

### 6.7 循环读流（77-100 行）—— 全页最核心

| 行 | 代码 | 解释 |
|---|---|---|
| 79 | `const { done, value } = await reader.read();` | 读一段：`done` = 结束了吗；`value` = 这段字节（§2③） |
| 80 | `if (done) break;` | 结束就跳出循环 |
| 83 | `buffer += decoder.decode(value, { stream: true });` | 这段字节翻译成文字，**追加**到 buffer |
| 86 | `const parts = buffer.split("\n\n");` | 按空行切帧 —— `split` ≈ Python `str.split`，返回**列表** |
| 87 | `buffer = parts.pop();` | 最后一段**可能不完整**，拿出来**留回 buffer**（§4①） |
| 90-99 | `for (const part of parts) { … }` | 逐个处理完整帧（≈ `for x in list`） |
| 92 | `if (!part.startsWith("data: ")) continue;` | 不是 `data: ` 开头就跳过（≈ `startswith` + `continue`） |
| 94 | `const piece = part.slice(6);` | 切掉前 6 个字符 `"data: "`，剩下是正文 |
| 95 | `if (piece === "[DONE]") continue;` | 收尾标记，跳过。`===` = 严格相等（不转类型） |
| 97 | `replyText += piece;` | 把这一小段**攒**起来 |
| 98 | `replyEl.textContent = "AI：" + replyText;` | 把攒好的文字**写进气泡** —— 页面上的字一个个蹦出来，就是这行每次循环都在重写 |

### 6.8 收尾入史（102-103 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 103 | `history.push({ role: "assistant", content: replyText });` | AI 完整回复存进历史 —— **下一轮的上下文就靠它** |

### 6.9 兜底与解锁（104-111 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 104-108 | `catch (err) { addBubble("AI：网络断了…"); console.error(err); }` | 上面任何一步抛错都跳这：留提示，错误打到浏览器控制台（`catch` ≈ `except`） |
| 109-111 | `finally { sendBtn.disabled = false; }` | **不管成功失败都执行**：解锁按钮（同 Python `finally`） |

## §4 三个难点深讲

### ① 为什么拆帧要「把最后半截留回 buffer」

网络数据**不保证按帧到达**：可能一次给你 1.5 帧。实测：

```
buffer = "data: 你\n\ndata: 好\n\ndata: [DO"
split("\n\n") → ["data: 你", "data: 好", "data: [DO"]
parts.pop()  → 尾巴 "data: [DO" 留回 buffer，只处理前两个完整的
```

下一批数据到了，尾巴接上新数据凑成完整帧再处理。**不留尾巴 → 半截帧被当完整帧 → 乱码/漏字。**

### ② TextDecoder 为什么要 `{ stream: true }`

中文一个字 = UTF-8 **3 个字节**，字节流可能正好把「你」切在两段中间。实测：

```
「你」的字节 = [228, 189, 160]
不带 { stream:true }：第一段 [228,189] → "�"    第二段 [160] → "�"    ← 两个乱码字符
带   { stream:true }：第一段 → ""               第二段 → "你"          ← 翻译机记住了「还差字节」
```

`{ stream: true }` = 「还没完，字节接不上先别乱猜，等下一批」。

### ③ try / catch / finally 各管什么（104-111 行）

- `try` = 正常流程（发请求、收流、写历史）
- `catch` = 任何一步出错走这里（后端挂了、网络断了）→ 给用户提示
- `finally` = **无论如何**都执行 → 按钮解锁。没有它：一出错按钮永远灰着，页面废掉
- 附带：`replyText` 声明在 `try` **外面**（第 55 行）—— `catch` 之后的 `history.push` 也要用它；写在 `try` 里，外面看不见（块级作用域）

## §5 事件绑定（114-121 行）

| 行 | 代码 | 解释 |
|---|---|---|
| 116 | `sendBtn.addEventListener("click", send);` | 「按钮被点击时调用 `send`」。**注意不带括号**：`send` = 把函数交给它（点击时你替我执行）；`send()` = 现在立刻执行 |
| 119-121 | `inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });` | 「键盘按下时」：按的是 Enter 就调 `send`。`(e) => {…}` 是匿名函数（≈ Python `lambda`，但可写多行）；`e` 是这次按键事件，`e.key` 是键名 |

## §6 自测（先自己答，答案在文末）

1. `const` 和 `let` 的区别？`history` 用 `const` 为什么还能 `push`？
2. `history.push(...)` 推进去的是什么结构？和 Python 的什么对应？
3. 第 87 行 `buffer = parts.pop();` 删掉，会出现什么现象？
4. 第 83 行去掉 `{ stream: true }` 会怎样？
5. 第 67 行 `if (!resp.ok)` 为什么必须有？
6. 第 116 行写成 `addEventListener("click", send())` 会怎样？
7. 第 109-111 行 `finally` 不写，什么场景下页面会废？
8. 第 55 行 `replyText` 为什么声明在 `try` 外面？

<details>
<summary>答完再看（点开）</summary>

1. `const` 绑定不能再赋值、`let` 可以；`push` 改的是**数组内容**，不是绑定，所以 `const` 可以。
2. `{role:"user",content:text}` = dict；推进 list —— 就是 Python 的 `list.append(dict)`。
3. 半截帧会被当完整帧处理 → 正文缺字/乱码。
4. 中文被切两半时输出两个乱码字符（实测 `"�"`）。
5. 非 2xx（如 500）时 `fetch` **不会自动报错**，不检查就会把错误响应当正常流读 → 空气泡。
6. 页面加载时立刻执行一次（发了请求），且把返回值 `undefined` 当回调 —— 之后点击按钮无反应。
7. 走到 `catch`（后端挂/网络断）之后按钮**永久禁用**，再也没法发消息。
8. `catch` 之后的 `history.push` 也要用它；`try` 内声明的变量外面看不见。

</details>

## §7 下一步

读完 → 把**讲不出的行号**贴给我（一个也行）→ 我补讲 → 抽查几行 → 进第 1 件（项目归位）。
