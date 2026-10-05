# 错题本（报错与踩坑）

> 规则见 `notes/README.md`：只在**同一个错犯第二次**或**某个报错让你意外**时记一条。
> 格式：报错原文 → 原因一句话 → 解法一句话。**这就是面试素材**（面试官问「你踩过什么坑」时直接讲）。

## 2026-09-22

### 1. `history` 里的字典键写错（**同类错第二次**）

```
openai.BadRequestError: 400 - {'code': 'BAD_REQUEST', 'message': 'messages.0.role 取值无效'}
```

- 原因：`history` 里每条消息必须是 `{"role": ..., "content": ...}` 两个键。当天两次写成别的：
  上午 `history.append({"assistant": reply})`（键名当成了 role 值）；下午 `/clear` 里 `history = [{"system": SYSTEM_PROMPT}]`。
- 解法：写任何往 `history` 里塞字典的代码前，先念一遍 **「role + content」**；API 的 400 文案里带 `messages.N.xxx` 就是在说第 N 条消息的结构不对。

### 2. 流式收尾块没有 `choices`，`chunk.choices[0]` 越界

```
File "llm.py", line 61, in ask
    piece = chunk.choices[0].delta.content
IndexError: list index out of range
```

- 原因：`stream=True` 时**最后一块只带 `usage`、`choices` 是空列表**（实测：0-3 号块 `choices:1`/`usage:None`，4 号块 `choices:0` + `CompletionUsage`）。`if chunk.choices[0] is None:` 不是兜底 —— 下标在判断之前就取了。
- 解法：`if not chunk.choices: continue`，并且**放在取完 `usage` 之后**（否则永远拿不到 token 数）。

### 3. `usage = 0` 漏写 → `UnboundLocalError`

```
UnboundLocalError: cannot access local variable 'usage' where it is not associated with a value
```

- 原因：`usage` 只在收尾块才被赋值；某次流里没有 usage 块（或流被截断）时，函数返回时就找不到这个名字。**概念答对了不等于代码写了。**
- 解法：循环前给 `usage = 0` 兜底。

### 4. 缩进 = 归属（换个地方又踩了一次）

```
（程序无任何输出，退出码 0）
```

- 原因：`if __name__ == "__main__": main()` 被缩进进了 `main()` 函数体内 → 变成「只有 main 被调用时才决定要不要调用 main」，而没人调用 main，整个文件只是定义了个函数。
- 解法：入口块必须**顶格（0 缩进）**、在函数外面。

## 2026-09-23

### 5. 日志字段名打错 → 程序不报错、文件却是空的（意外）

```
--- Logging error ---
KeyError: 'asctimeds'
ValueError: Formatting field not found in record: 'asctimeds'
```

- 原因：`format` 里的 `%(xxx)s` 必须是日志记录对象上**真实存在的字段名**（`asctime` / `levelname` / `name` / `message`）。写错时 `logging` **不崩程序** —— 它把错误打到 stderr，然后**丢掉这条日志**，于是表现为「程序正常跑完、`chat.log` 0 字节」。
- 解法：改完先看**终端输出**、再看文件；文件空 ≠ 代码没跑。

### 6. 文件名大小写（**同类错第二次**：09-18 的 `readme.md` → 今天的 `README.MD`）

```
week04/README.MD        ← 已 commit 才发现
```

- 原因：Windows 文件系统大小写不敏感，本地怎么敲都能打开，看不出问题；Linux / CI 上 `README.MD` ≠ `README.md`，按小写找文件的脚本会找不到。
- 解法：新建文件名一律小写（全仓其他 README 都是小写）；已提交的用 `git mv 旧名 新名` 改（实测 Windows + Git Bash 可用）。

## 2026-09-27

### 7. `try` 里的初始化 + `try` 外的读取 → 坏 key 时流被截断（**同类第 2 次**：09-22 的 `usage = 0`）

```
UnboundLocalError: cannot access local variable 'token' where it is not associated with a value
（客户端现象：收到 [错误] 帧后连接就断，[DONE] 都收不到）
```

- 原因：`token = None` 写在 `try` 里、`yield f"...{token}..."` 写在 `except` **之后** —— `create()` 抛错时赋值从没执行，读它直接崩；崩点在 `except` 之外，接不住。
- 解法：**读点在 `try` 之后，初始化就必须在 `try` 之前**；发帧前再判 `if token is not None:`（区分「没收到」与「收到 0」）。

### 8. 相对路径不是「相对文件」，是「相对启动命令所在目录」（意外）

```
RuntimeError: Directory 'week07/chat_web/static' does not exist
```

- 原因：`StaticFiles(directory="week07/chat_web/static")` 在模块顶层执行，相对的是**启动服务时所在的目录**；换个目录启动（或部署到别处）当场崩，不是 404。
- 解法：要锚定「文件自己在哪」就用 `Path(__file__).parent / "..."`。

## 2026-09-28

### 9. 脚本放错目录 → `glob` 空结果、**静默无报错**（意外）

```
（无 Traceback：清洗前后打印全是空列表，代码怎么查都"没错"）
```

- 原因：`loader.py` 被放进了 `data/` 目录里 → `DATA_DIR = Path(__file__).parent / "data"` 实际指向 `data/data`（不存在）→ `glob` 找不到文件返回空列表，**程序不报错**。
- 解法：脚本放 `projects/rag-kb/`、语料放 `projects/rag-kb/data/`；排查「空结果」第一步先 `print(DATA_DIR)` 看程序到底在哪个目录找文件。

### 10. 对字典数长度得到个位数——手里拿的是「键」不是「值」（意外）

```
（无报错：len() 打印出 4、6 这种个位数）
```

- 原因：`docs` 里装的是**字典**（`{"source": ..., "text": ...}`）。`for x in 字典` 拿到的是**键名**（`"source"`/`"text"`，长度 6 和 4）；`len(字典)` 是键的个数（2）。
- 解法：取内容必须 `doc["text"]`；看到长度是 4/6 这种个位数，先问自己「我手里到底是字典还是值」。

## 2026-09-29

### 11. `except` 接住错误后，代码继续往下跑 → 用上没赋值的变量，第二次报错（**同类第 3 次**：09-22 `usage = 0`、09-27 `token = None`）

```
第一次报错（被 except 接住）: overlap 必须大于等于 0
Traceback (most recent call last):
  File "<string>", line 9, in <module>
    for num, chunk in enumerate(chunks):
NameError: name 'chunks' is not defined
```

- 原因：`chunks = split_text(...)` 写在 `try` 里，抛错时赋值从未发生；`except` 只是**接住**了那个错误，**它后面的代码照常往下跑** —— 遍历一个不存在的名字，于是第二次崩。
- 解法：把「用 `chunks`」的代码放进 `else:`（只在 try 成功时才执行）。记一句：**except 不是终点**。

### 12. 函数参数被写死 → 所有向量都成了同一句话的向量，相似度全是 1（**意外**；老毛病「把字面量写死」的新形态）

```
（无报错：不同问题、不同块的相似度全部打印 1.0）
```

- 原因：`embed(text)` 里的调用写成了 `input="怎么报销差旅费"`，**没用参数 `text`** —— 不管传什么进去都返回同一句话的向量，两个相同向量余弦 = 1。
- 解法：函数体里出现字面量时问一句「这个值该不该来自参数」；看到「所有相似度相同 / 全是 1」先查「是不是所有输入被换成了同一段文本」。

## 2026-10-05

### 13. 脚本里用「相对当前目录」的路径读文件（**同类第 2 次**：09-27 #8 —— 相对路径算错基准）

```
FileNotFoundError: [Errno 2] No such file or directory: 'projects/rag-kb/samples/报销制度.pdf'
```

- 原因：脚本里写 `"projects/rag-kb/..."` 是相对**你敲命令时所在的目录**算的，不是相对脚本文件——在 `projects/` 下跑就多叠一层 `projects/`，找不到。（同一次修里还叠了第二层：新写法加了、**旧行没删**——同名变量被下面那行旧的覆盖，报错看起来「修了没效果」。）
- 解法：脚本找自带文件一律 `HERE = Path(__file__).parent` 再拼（`HERE / "samples" / "..."`）；改代码是**替换**不是叠加——改完扫一眼旧写法还在不在。
