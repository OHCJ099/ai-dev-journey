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
