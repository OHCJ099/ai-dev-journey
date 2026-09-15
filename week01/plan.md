# W01（2026-09-15 周二 ~ 09-21 周一）Python 复习 + 环境 + 首次调用 DeepSeek API

**本周唯一硬目标：周末结束前，你自己的仓库里有 `chat_cli` v0.1 —— 命令行里能和大模型流式多轮对话，支持切换 system 角色。**
（第 1 周不碰 RAG、不碰 LangChain，地基先夯实。）

时间总量约 16 小时。

---

## Day 1｜周二 09-15（1.5h）环境三件套 + 建仓库

**学**：uv 是什么（替代 pip/venv 的现代包管理器）；Git 三区（工作区/暂存区/本地库）。

**做**
1. 校验已装工具（这台机器已具备）：
   ```bash
   python --version     # 3.12 / 3.14 均可
   uv --version         # 0.12.7
   git --version        # 2.53
   code --version       # VS Code
   ```
   缺哪个补哪个：Python → https://www.python.org/downloads/ ；uv → `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` ；Git → https://git-scm.com/download/win
2. VS Code 装 3 个扩展：`Python`(ms-python.python)、`Ruff`(charliermarsh.ruff)、`Even Better TOML`。
3. 建仓库并跑通第一条命令：
   ```bash
   cd ~/ai-dev-journey
   git init
   uv init --no-workspace
   uv add openai python-dotenv httpx
   uv run python -c "import openai, sys; print(sys.version, openai.__version__)"
   ```
   能打印出版本号 = 环境通了。
4. 写 `.gitignore`（至少含 `.env`、`__pycache__/`、`.venv/`），`git add . && git commit -m "chore: init repo with uv"`。
5. GitHub 上建空仓库 `ai-dev-journey`（Public），然后：
   ```bash
   git remote add origin https://github.com/<你的用户名>/ai-dev-journey.git
   git branch -M main && git push -u origin main
   ```
   （第一次 push 会弹浏览器授权，按提示登录即可。）

**验收**：GitHub 网页上能看到你的 commit；`uv run python -c "import openai"` 无报错。
**资源**：uv 文档 https://docs.astral.sh/uv/ ；B 站搜「uv 包管理 教程」。

---

## Day 2｜周三 09-16（2h）Python 复习 I：数据结构与流程

**学**（只读这两章，1 小时够了）
- 官方教程中文版 3-5 章：https://docs.python.org/zh-cn/3/tutorial/
- 重点：`list` / `dict` 的增删查改、`for`/`while`、`if`、字符串 `f-string`、推导式、`enumerate`/`zip`。

**做**（1h，写进 `week01/contacts.py`）
实现一个控制台通讯录：`add 张三 138xxx` / `list` / `find 张` / `del 3` / `quit`，数据存到 `contacts.json`（自己先查 `json` 模块怎么用）。
- 不许用第三方库，纯标准库。
- 数据用 `list[dict]` 存：`[{"name": "张三", "phone": "138xxx"}]`。

**验收**：退出脚本再运行，`list` 还能看到之前加的人。卡在文件读写就直接查 `json.dump` / `json.load` 的参数。
**资源**：B 站「Python 基础 廖雪峰 / 黑马程序员 Python」；遇到不认识的写法先 `python -c "help(list.append)"`。

---

## Day 3｜周四 09-17（2h）Python 复习 II：函数、模块、异常

**学**
- 函数：默认参数、`*args/**kwargs`、返回值、作用域。
- 模块化：`from x import y`、`if __name__ == "__main__":`。
- 异常：`try/except/else/finally`、`raise`、自定义异常。
- 类型注解：`def f(name: str) -> dict[str, str]:`，以及为什么工程里必须写。

**做**（1.5h，重构 Day 2 的代码）
- 拆成 `week01/contacts/__init__.py`、`storage.py`（只负责读写 json）、`core.py`（业务逻辑：增删查）、`cli.py`（只负责输入输出与参数解析）。
- 所有函数加类型注解；文件读写加 `try/except FileNotFoundError / json.JSONDecodeError`。
- `cli.py` 用 `argparse` 支持 `python cli.py add --name 张三 --phone 138` 这种一次性命令。

**验收**：`uv run ruff check week01/` 无报错；`storage.py` 里没有 `print`（分层清楚）；故意把 json 文件改坏，程序给出友好提示而不是崩溃堆栈。

---

## Day 4｜周五 09-18（2h）Python 复习 III：文件路径、环境变量、HTTP

**学**
- `pathlib.Path` 优于字符串拼路径（Windows 反斜杠坑）。
- `os.getenv` + `python-dotenv`：`load_dotenv()` 读 `.env`。
- 类：只需要会写「有 `__init__` 和几个方法」的类，不用深入继承/魔术方法。
- `httpx`：`httpx.post(url, json=..., headers=...)`、超时参数、`resp.raise_for_status()`、`resp.json()`。

**做**（1.5h，写进 `week01/http_demo.py`）
1. 用 `httpx` 调一个免费公开 API（如 https://httpbin.org/get 或 https://api.github.com/users/<你的名字>），打印状态码和 JSON 里某个字段。
2. 加 5 秒超时 + `try/except httpx.TimeoutException`。
3. 建 `week01/.env`，写 `DEMO_KEY=abc`，用 `load_dotenv()` + `os.getenv` 读出来打印；`.env` 不要提交（确认 `.gitignore` 已生效：`git status` 里看不到它）。

**验收**：`git status` 不显示 `.env`；能解释「为什么 key 不能写进代码」。

---

## Day 5｜周六 09-19（3.5h）第一次调用大模型 API（本周重点）

**准备**
1. DeepSeek 开放平台 https://platform.deepseek.com/api_keys 创建 API Key，充值 10-20 元（够用很久）；把 key 写进 `week01/.env`：`DEEPSEEK_API_KEY=sk-xxx`。
2. 读官方「首次调用 API」：https://api-docs.deepseek.com/zh-cn/
   - `base_url = "https://api.deepseek.com"`，OpenAI 兼容格式
   - 模型名：**`deepseek-flash`**（便宜快）/ `deepseek-v4-pro`（更强）
3. 备用（有免费额度）：通义千问百炼 https://help.aliyun.com/zh/model-studio/ ，`base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"`，模型 `qwen-plus`，key 环境变量 `DASHSCOPE_API_KEY`。两家的 SDK 用法完全一样，只换 base_url / model / key。

**做**（step by step，每步先自己写再看答案）
1. `week01/hello_api.py`：用 `openai` SDK 发一次非流式请求，`print` 出回复内容 + `resp.usage`（prompt/completion/total tokens）。
2. 改成 `stream=True`，用 `for chunk in stream:` 逐字打印（注意 `chunk.choices[0].delta.content` 可能是 `None`，要判断）。
3. 加上 `messages` 多轮：先订一个 `messages` 列表，`system` 定角色（例："你是我的 Python 助教，回答不超过 3 句"），循环里把用户输入 append 成 `{"role":"user","content":...}`、把模型回复 append 成 `{"role":"assistant",...}`，验证它记得上一轮说的话。
4. 故意把 key 改错，观察异常类型，用 `except Exception as e: print("调用失败:", e)` 包起来；再试一个不存在的模型名，看报什么错。

**验收**（口头能答上来才算过）
- `messages` 里 `system/user/assistant` 三种 role 分别是什么作用？
- `temperature` 调高调低分别什么效果？
- `stream=True` 的返回和 `False` 的返回差在哪？
- `usage.total_tokens` 大概一次对话花多少钱？（去定价页算一次）

---

## Day 6｜周日 09-20（3.5h）迷你项目：chat_cli v0.1

**目标**：一个能长期用、能放进简历第 1 条的 CLI 聊天工具。目录 `week01/chat_cli/`：

```
chat_cli/
├── README.md          # 一句话定位 + 运行方法 + 截图(可选)
├── pyproject.toml     # 由 uv 生成
├── .env.example       # DEEPSEEK_API_KEY=your_key_here
├── .gitignore
└── src/
    ├── llm.py         # 封装 LLM 客户端：一个类，方法 chat(messages) -> str，支持流式
    ├── session.py     # 管理 messages 历史（含 system prompt、/clear、/system 指令）
    └── main.py        # CLI 循环：读输入 -> 调 LLM -> 打印
```

**功能需求（必须全做到）**
1. 流式输出（逐字打印，有打字机效果）。
2. 多轮上下文；`/clear` 清空历史；`/system 你现在是一个 SQL 专家` 动态换角色；`/exit` 退出。
3. 报错不崩：网络超时、401（key 错）、余额不足，都给中文友好提示并允许继续输入。
4. 每次回复后打印本次 token 消耗与累计消耗。
5. 历史导出：`/save` 把当前会话存成 `sessions/2026-09-20-1530.json`。

**实现要求**
- 自己先写，卡住超过 25 分钟再翻参考实现：`week01/chat_cli_reference.py`（同一目录，别复制粘贴整份，只挑你不会的那段）。
- 关键设计：`llm.py` 里不许出现 `input()`/`print()`，`main.py` 里不许出现 `http`/`openai`。这条分层是面试常问点。

**验收**：`cd week01/chat_cli && uv run python src/main.py` 能连续对话 10 轮不走样；`/clear` 后模型确实忘了之前内容；拔网线/断代理时报错但不退出。

---

## Day 7｜周一 09-21（1.5h）验收 + 复盘 + 推 GitHub

1. 跑一遍 Day 6 全部验收项，逐条打勾。
2. `git add . && git commit -m "feat: chat_cli v0.1 streaming multi-turn CLI"` 并 push；README 补齐「功能 / 运行步骤 / 技术栈 / 我踩的坑」。
3. 在 `README.md` 的周进度表里填 W01 一行：产出 + 卡点。
4. 写 3 句话周报发给教练（我）：① 完成了什么 ② 最卡的一个点 ③ 下周想先做哪个方向。
5. 存一个「错题本」文件 `notes/gotchas.md`，把本周所有报错原文 + 原因 + 解法记进去（这是面试素材）。

---

## 本周明确的「不要做」
- 不要装 LangChain / 不要碰 RAG / 不要学 FastAPI（第 2 月才用）。
- 不要追求把 Python 学完，够用就往前走 —— 后面的项目会反复用到，边做边补。
- 不要为了「看懂原理」去读 transformer 论文。

## 卡住时的最小可执行动作
1. 把完整报错原文贴给我（连 traceback 最后 5 行），并说明你期望的结果。
2. 只缩小到 5 行以内能复现的代码。
3. 卡点超过 40 分钟就问我，别死磕 —— 但先自己查 15 分钟文档。
