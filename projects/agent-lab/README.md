# agent-lab —— 项目③（Agent）

早期教学入口（W17、W18）：

- `tools_demo.py` —— **W17**：四个工具 + 单轮 `function calling`（模型选工具 → 程序执行 → 模型汇总）
- `react_loop.py` —— **W18**：手写 ReAct 多步循环（Thought → Action → Observation → 再 Thought），带终止条件、最大步数、错误喂回、重试上限

## 四个工具契约

| 工具名 | 入参 | 返回 | 说明 |
|---|---|---|---|
| `multiply` | `a: number`、`b: number` | `a * b`（数字） | 乘法 |
| `divide` | `a: number`、`b: number` | `a / b`（浮点数） | `b == 0` 时抛 `ValueError("除数不能为 0")` |
| `count_chars` | `text: string` | 字符数（整数） | 用 `len()`，一个汉字算 1 |
| `get_weather` | `city: string` | `<城市>, 晴, 25℃`（字符串） | 假数据，不联网 |

工具名必须与 `TOOLS` 里 `function.name` 逐字一致；`TOOLS_BY_NAME` 靠这个名字找函数，找不到走兜底。**加新工具要改三处**：函数本身、`TOOLS` 里的 schema（给模型看的说明书）、`TOOLS_BY_NAME` 的映射。

## 怎么跑

以下命令都在仓库根目录下执行。`react_loop.py` 用 `from tools_demo import ...`，依赖同目录可导入。

### W17：单轮 function calling

```powershell
cd D:\dev\ai-dev-journey
uv run python projects/agent-lab/tools_demo.py
```

跑两个用例：一个是三个并行工具调用，一个是不需要工具的普通问答。

### W18：ReAct 多步循环

```powershell
cd D:\dev\ai-dev-journey
uv run python projects/agent-lab/react_loop.py
```

任务是「先算 12 乘 8，再把结果除以 4」，预期三步：`multiply` → `divide` → 出最终答案。每一步打印 `finish_reason` / `Thought` / `Action` / `Observation`。

调参：`MAX_STEPS`（最大循环步数，默认 8）、`MAX_RETRIES`（同一工具连续失败上限，默认 3）。把 `MAX_STEPS` 压到 2 可以复现「步数用尽」路径。

需要 `.env` 里有 `DEEPSEEK_API_KEY`（模型端点 `https://api.deepseek.com/v1`）。

## ReAct 循环的退出条件

| 出口 | 触发条件 | 性质 |
|---|---|---|
| 正常出口 | `finish_reason == "stop"` | 模型自己说「不需要工具了」 |
| 保险出口 | `step >= MAX_STEPS` | 程序兜底，防死循环烧 token；**打印「步数用尽」，不静默返回半成品** |
| 重试出口 | 同一工具连续失败 `MAX_RETRIES` 次 | 防模型死磕一个坏调用；设 `done = True` 后 `break` 出内层 `for`，靠 `while ... and not done` 退出 |

不能只靠 `finish_reason` 退出：那个 `"stop"` 是模型自愿给的。工具持续报错时模型每轮都是 `tool_calls`，永远等不到 `stop`，只能靠程序侧的步数上限。

**重试 vs 换工具**：重试由**程序**计数（`fail_counts[name]`），换工具由**模型**自己决定（下一轮自己换 `name` 或改参数），程序从不替模型选工具。

## W19：LangGraph 版 Agent（`langgraph_agent.py`）

```powershell
cd D:\dev\ai-dev-journey
uv run python projects/agent-lab/langgraph_agent.py
```

同一个「12×8÷4」任务用状态机重写：`agent` 节点决定调什么工具 → `tools` 节点执行 → 回到 `agent`，直到模型不再要 `tool_calls`。

**它比 `react_loop.py` 多了三层保险**（W19-D2/D3 补的）：

| 层 | 在哪 | 挡什么 |
|---|---|---|
| `handle_tool_errors=True` | `ToolNode(...)` | 工具执行期异常 / 工具名错 / 参数错 → 转成 `status="error"` 的 `ToolMessage` 喂回模型 |
| 按工具名计数的熔断 | `agent()` 开头（`fail_counts`） | 同一工具连续失败 3 次 → 造一条无 `tool_calls` 的 `AIMessage` 收工 |
| `recursion_limit` | `invoke/stream` 的 config | 兜底，防总步数失控 |

**`fail_counts` 为什么按名字分桶**：只数「连续 error」会被别的工具的成功截断（`divide` 连败 4 次，中间夹一次 `multiply` 成功就永远数不到 3）。按 `name` 分桶后，`multiply` 成功只清 `multiply` 自己的账。**扫描必须正序**，倒序会把最近的成功当开头，把成功之前的旧失败全算成「连续」。

**短期记忆**：`g.compile(checkpointer=MemorySaver())`，`invoke` 时传 `{"configurable": {"thread_id": "..."}}`。

- 同一个 `thread_id` → `state["messages"]` 累积该 thread **全部历史**（第 2 轮「刚才那个结果再加 10」能答出 34，是因为历史里有 `tool: 24.0`，不是模型自己记得）
- 换 `thread_id` → 全新状态，答不出
- `MemorySaver` 存在**进程内存**，脚本退出即丢

**config 是两层，别叠错**：

```python
# config 是两层，thread_id 在内层，recursion_limit 在外层
{
    "configurable": {"thread_id": "A"},
    "recursion_limit": 10,
}
```

把 `recursion_limit` 塞进 `configurable` 里 **不报错、不警告、静默失效**（实测）。只给 `recursion_limit` 不给 `thread_id` 则抛 `ValueError: Checkpointer requires ... thread_id`。

**两个脚本都要 `.env` 里的 `DEEPSEEK_API_KEY`**（模型端点见 `.env` 的 `DEEPSEEK_BASE_URL`，默认 `http://127.0.0.1:8787/v1`）。

## W20：项目③ 多工具 Agent（`multi_tool_agent.py`）

把项目② 的 RAG 检索包成工具，和 `multiply` 一起交给模型自行编排 —— 这是**项目③ 的主体**，不是教学样例。

```powershell
cd D:\dev\ai-dev-journey
uv run python projects/agent-lab/multi_tool_agent.py
```

### 一、两个工具的契约

| 工具名 | 输入 / 返回 | 什么时候会被调用 |
|---|---|---|
| `search_kb` | `(question: str) -> str` | 问题涉及公司制度、规章、请假、报销等**需要查文档才能答**的内容时（模型自己判断「我不知道，得查」） |
| `multiply` | `(a: float, b: float) -> str` | 任何涉及两数相乘的算式时（模型不自己口算，实测「3乘4」→ 1 次 tool_call）；闲聊时**不调用** |

**两边都是 `-> str` 不是巧合**：`ToolNode` 会把任何返回值转成字符串再塞进 `ToolMessage`（实测返回 `list` 得到 `'[["请假制度.md", "年休假5天"], ...]'`），所以返回 str 是**选择**而非限制。

**`search_kb` 为什么自己拼字符串、不返回 `hits` 列表**：拼好的形式是

```
[1]请假制度.md：，年休假5天；已满10年不满20年的，年休假10天…

[2]薪酬制度.md：…
```

每条带编号、带来源、条目间有空行。若直接返回列表，喂给模型的是 `'[["请假制度.md", "年休假5天"], ...]'` —— 编号没有、正文和来源挤在一个 JSON 串里，模型得先解析再理解。**格式在工具里定好，模型就不用猜。**

（文件位置：`projects/agent-lab/rag_tool.py`、`tools_demo.py` 的 `multiply`）

### 二、复合任务的调用链

同一句问话，模型**可能拆成并行、也可能拆成串行**，两种都实测到过。

**并行**（1 次进 `agent` 就带两个调用，共 5 条消息）：

```
human  查一下年假有几天，然后算一下如果我有 3 天没休，能折算多少钱，每天 300 元
ai     我来先查一下年假制度，同时算一下 3 天的折算金额。  tool_calls=['search_kb', 'multiply']
tool   [1]请假制度.md：，年休假5天；…
tool   900.0
ai     根据制度查到的结果，回答如下：…
```

**串行**（两次进 `agent`，每次 1 个调用，共 6 条消息）：

```
human  同一句话
ai     我先查一下年假制度。              tool_calls=['search_kb']
tool   [1]请假制度.md：…
ai     找到了年假规定。现在算一下折算金额。  tool_calls=['multiply']
tool   900.0
ai     根据制度查到的结果，回答如下：…
```

两个要点：

1. **「ai 回应」和「ai 调工具」是同一条消息**。`AIMessage` 有 `content`（说的话）和 `tool_calls`（要做的事）两个字段，打印时若只打 `content` 就看不见 `tool_calls` —— 会误以为它们是两条。
2. **哪条 `ToolMessage` 属于哪个调用，靠 `tool_calls[i]["id"]` ↔ `tool_call_id` 对应，不靠顺序**。

**并行时谁能并行**：一条 `AIMessage` 的 `tool_calls` 里可放 N 个调用；`ToolNode` 会**并发执行同一批**（实测两个各 `sleep(2)` 的工具，总耗时 2.01s 而非 4s）。但**模型这一轮怎么拆是不保证的** —— 同一句话两次跑，并行/串行都出现过。

## 已知限制

### `tools_demo.py`（W17）

- 只做**一轮** `tool_calls` → 一次汇总调用。模型如果连续两轮都在调工具，第二次的结果会被忽略（答案打印为空）。W18 的 `react_loop.py` 已用 `while` 循环解决。
- 工具执行没有 `try`：工具内部抛异常会直接崩掉脚本。

### `react_loop.py`（W18）

- **模型返回坏 JSON 会让程序崩掉**：`json.loads(tc.function.arguments)` 在 `try` 外面（约第 54 行），`except Exception` 接不住 `JSONDecodeError`。修法是把 `json.loads` 移进 `try`，把解析失败也当成一条 `ERROR ...` 的 observation 喂回模型。**（W19-D2 已修：`json.loads` 移入 `try`，坏 JSON ×3 → 第 3 次终止、exit 0 不崩。）**
- 单个任务单轮执行，没有对话记忆（多轮记忆在 W19）。**（W19 已提供 `langgraph_agent.py` + `MemorySaver`；本文件保留为手写版对照。）**
- 没有 async，没有 LangGraph（W19 用框架重写一遍这个循环）。
- 工具执行串行，并行 `tool_calls` 是一个个跑的。

### `memory_agent.py`（W19 单节点最小版）

- 只有一个 `chat` 节点、一次调用就结束 —— 用它看 `StateSnapshot` 字段最干净，但**它不是 Agent**，没有工具、没有循环、没有熔断。
- 记忆同样只在进程内（`MemorySaver`）；没有长期记忆、没有偏好存储（留 W20 或项目③收尾）。

### `langgraph_agent.py`（W19）

- `MemorySaver` 在**进程内存**，脚本退出即丢；要跨进程得换 `SqliteSaver` / `PostgresSaver`（未做）。
- `fail_counts` 是**每轮从完整历史重算**的，历史越长每轮扫得越久；真实长对话需要「只扫最近 N 条」或把计数存进 state 字段（未做）。
- 没有 `interrupt` / 人工确认节点；没有 async。

### `multi_tool_agent.py`（W20）

**① `ensure_index` 只判空、不判完整性**

- 现象：`index_store.py:32` 只有 `if count > 0: return count`，剩 1 块也当完整。
- 触发：索引目录被部分删除、`COLLECTION_NAME` 改过又改回、`ingest_file` 中途 Ctrl+C。
- 后果：库残缺却静默返回块数，检索结果变少或变错，**不报错**——比崩溃更难发现。

**② `fail_counts` 每轮从完整历史重算**

- 现象：`agent()` 开头每次都从头扫 `state["messages"]`。
- 触发：每进一次 `agent` 节点。
- 后果：对话越长越慢（每轮 O(n)，整轮累计 O(n²)）。

**③ `MemorySaver` 只在进程内存**

- 现象：`g.compile(checkpointer=MemorySaver())`。
- 触发：脚本退出 / 进程结束。
- 后果：`thread_id="A"` 的全部历史丢失，无法跨进程续聊；要持久化需换 `SqliteSaver`。

### 目录里的其他文件

`practice/` 放的是 W19 学习期的探针与最小图（`w19a_two_nodes.py` 两节点黑板、`w19a_conditional.py` 条件边、`probe_graph.py` / `probe_limit.py` / `probe_llm.py`），只用于回顾，不是项目入口。