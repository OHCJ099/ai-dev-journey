# agent-lab —— 项目③（Agent）

两个文件，对应两个阶段：

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

两个文件都在仓库根目录下执行。`react_loop.py` 用 `from tools_demo import ...`，依赖同目录可导入。

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

## 已知限制

### `tools_demo.py`（W17）

- 只做**一轮** `tool_calls` → 一次汇总调用。模型如果连续两轮都在调工具，第二次的结果会被忽略（答案打印为空）。W18 的 `react_loop.py` 已用 `while` 循环解决。
- 工具执行没有 `try`：工具内部抛异常会直接崩掉脚本。

### `react_loop.py`（W18）

- **模型返回坏 JSON 会让程序崩掉**：`json.loads(tc.function.arguments)` 在 `try` 外面（约第 54 行），`except Exception` 接不住 `JSONDecodeError`。修法是把 `json.loads` 移进 `try`，把解析失败也当成一条 `ERROR ...` 的 observation 喂回模型。
- 单个任务单轮执行，没有对话记忆（多轮记忆在 W19）。
- 没有 async，没有 LangGraph（W19 用框架重写一遍这个循环）。
- 工具执行串行，并行 `tool_calls` 是一个个跑的。