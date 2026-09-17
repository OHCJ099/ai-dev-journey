# 六个月蓝图 v2（总指挥官版本）

> 用法：这份文件是**总纲**。每个阶段开一个新对话当「子教练」，提示词在 `handbook/`。
> 进度台账：`progress.md`（每个学习日由子教练追加一行）。验收标准见 `handbook/06-验收协议.md`。
> 学员坐标看文末「当前坐标」。

## 一、总目标与硬指标

6 个月内做出 **3 个可演示项目**（对话应用 → RAG 知识库问答 → Agent 多工具任务），能投递初级 AI 应用工程师。

唯一的硬指标：**不看答案，你能写出多少。** 抄得再多不算数。

每周 15-20 小时，全程约 400 小时。

## 二、26 周排期（每格都有交付物和验收）

| 周 | 阶段 | 学什么 | 交付物 | 验收标准 |
|---|---|---|---|---|
| W1 | ① Python 基础 | 环境/uv/git、list/dict/循环/if、文件 IO、异常 | `week01/contacts.py`（增删查+json 持久化） | 能不看代码讲清每行；能改一处加功能 |
| W2 | ① | 函数、模块分层、类型注解、`pathlib`、`.env`、`httpx` | contacts 拆成 `storage/core/cli`；`notes/` 错题本 | `ruff check` 无错；分层清楚（storage 里没有 print） |
| W3 | ② 大模型 API | DeepSeek API 首调、流式、messages/role、token 与成本、错误处理 | `week03/hello_api.py` + `chat_cli` v0.1 | 能口答 system/user/assistant、temperature、stream 的差别；401/超时都不崩 |
| W4 | ② | 多轮上下文管理、历史裁剪、参数化（argparse）、日志 | `chat_cli` v1 完整版 + README | 连续 10 轮对话不走样；`/clear` `/system` `/save` 可用；有 token 统计 |
| W5 | ③ Prompt + 后端 | Prompt 基础：角色设定、少样本、结构化输出(JSON)、温度实验 | `week05/prompt_lab.py`（同一问题的多 prompt 对比） | 能讲清每种手法的适用场景；实验有输出对比表 |
| W6 | ③ | FastAPI 最小：GET/POST、pydantic 模型、uvicorn | 把对话能力包成 `/chat` 接口 | `curl` 能调通；能讲清「接口」和「函数」的区别 |
| W7 | ③ | 前端最小页（单 HTML + fetch 流式/SSE） | `chat_web`（浏览器聊天页） | 浏览器里能连续聊天、有流式效果 |
| W8 | ③ | 项目①定稿：README、演示、错误兜底、成本控制 | **项目①：带 Web 界面的多轮对话应用** | 别人照着 README 能跑起来；能 3 分钟讲清架构 |
| W9 | ④ RAG（核心） | 文档加载与切分（chunk 策略）、清洗 | `projects/rag-kb/` 雏形 | 能讲清 chunk 大小/重叠怎么选，切分结果能人工检查 |
| W10 | ④ | Embedding 与向量库（Chroma）；相似度与检索 | 能对文档提问并召回片段 | 能讲清向量检索原理（不要求数学推导）；召回质量有主观判断标准 |
| W11 | ④ | 拼上下文、引用来源、防幻觉、拒答 | 带引用来源的问答 | 答案能标出处；资料里没有的问题会说「不知道」 |
| W12 | ④ | 检索优化：多路召回/重排/查询改写；评估集 | 20 条问题→答案的评估集 + 命中率 | **有数字**：命中率/正确率前后对比 |
| W13 | ④ | 工程化：上传文档、索引管理、增量更新 | 可上传文档的知识库服务 | 上传新文档后能被检索到；删除后不再召回 |
| W14 | ④ | 前端 + 接口（复用 W6-W7） | 知识库问答 Web 应用 | 浏览器可上传、提问、看引用 |
| W15 | ④ | 调优与成本：token 花费、缓存、失败案例分析 | 优化记录（前后对比） | 能讲清 3 个失败案例的原因和修法 |
| W16 | ④ | 部署：局域网/内网穿透/云主机；演示录屏 | **项目②：知识库问答（可访问）** | 有可访问链接（或录屏）+ README + 架构图 |
| W17 | ⑤ Agent | Function calling / 工具调用协议 | `week17/tools_demo.py`（手写 2-3 个工具） | 能讲清模型是怎么"决定"调用工具的 |
| W18 | ⑤ | 手写 ReAct 多步循环、错误重试 | 能多步完成任务的脚本 | 能讲清循环终止条件、防止死循环 |
| W19 | ⑤ | LangGraph 状态机、记忆（短期/长期） | LangGraph 版 Agent | 能讲清状态图和手写循环的差别 |
| W20 | ⑤ | 接上 RAG（把项目②当工具）、多工具编排 | **项目③：多工具 Agent** | 能自主「查知识库→调工具→汇总」完成一个复合任务 |
| W21 | ⑥ 工程化 | 配置/日志/超时重试/限流/成本、pytest 基础 | 三个项目统一工程规范 | 有测试、有日志、有错误兜底 |
| W22 | ⑥ | Docker 基础 + 部署到一个公网可访问的地方 | 项目②或③公网链接 | 链接能打开、能用 |
| W23 | ⑥ 求职 | 简历（1 页）、项目描述量化、GitHub 主页整理 | 简历 + GitHub 整理完 | 每个项目有：一句话定位/截图/技术栈/难点 |
| W24 | ⑥ | 面试题库（RAG 流程、评估、成本、失败排查）+ 模拟面试 | 30 个高频问题能答 | 模拟面试能过 80% |
| W25-26 | ⑥ | 投递、复盘被拒原因、补短板 | 投递记录表 + 复盘文档 | 每周投递量达标；根据反馈补 1-2 个短板 |

## 三、为什么第 1 个月要写「通讯录」这种土程序

因为**它就是 RAG 项目的骨架**，只是把「人」换成了「文档片段」：

| 通讯录里的写法 | 在 RAG 知识库问答里对应什么 |
|---|---|
| `contacts = []` | `chunks = []` 切好的文档片段集合 |
| `add 张三 138` | 往知识库里添加一份文档 |
| `{"name":"张三","phone":"138"}` | `{"text":"...","source":"手册.pdf","vector":[...]}` |
| `find 李`（名字含「李」即命中） | **检索** —— RAG 的心脏 |
| `del 1` | 删除某个文档/片段 |
| `json` 存盘、下次还能读 | **持久化**向量库/索引 |
| `try/except` 不崩 | API 超时/余额不足/限速处理 |
| 拆成 `storage/core/cli` | 项目分层（面试必问） |

一句话：用你完全能理解的数据，把后面要用的零件先过一遍手。

## 四、每天的三步法（防「抄完什么都没学」）

1. **抄**：照着写一遍，建立手感
2. **讲回**：用自己的话把每行讲一遍（最容易跳过，最值钱）
3. **改**：改一处或加一个小功能（从「复制」变成「写出」）

时间分配：理解/讲回 30 分钟 + 动手 90 分钟。宁可少写一个功能，也要把抄过的讲清楚。

## 五、资源清单（只用这些，别再找第四个来源）

- 廖雪峰 Python 教程 https://liaoxuefeng.com/books/python/introduction/index.html
- Python 官方中文教程 https://docs.python.org/zh-cn/3/tutorial/index.html
- uv 文档 https://docs.astral.sh/uv/
- DeepSeek API 文档 https://api-docs.deepseek.com/zh-cn/ （模型名 `deepseek-flash` / `deepseek-v4-pro`）
- 通义千问（备用，有免费额度）https://help.aliyun.com/zh/model-studio/ （base_url `https://dashscope.aliyuncs.com/compatible-mode/v1`，模型 `qwen-plus`）
- FastAPI 文档 https://fastapi.tiangolo.com/zh/
- Chroma 文档 https://docs.trychroma.com/
- LangGraph 文档 https://langchain-ai.github.io/langgraph/
- 中文 Agent 系统教程（RAG/LangGraph/面试题，2026 更新）https://github.com/didilili/ai-agents-from-zero
  —— **按需检索、禁止通读**。映射：W3-W8 用 `01-1`/`01-3`；W9-W16 用 `04-1`~`04-5`；W17-W20 用 `03-1`/`03-2`；跳过 `02`（Coze/Dify 低代码）与 `05`（微调）
- 面试向 RAG+Agent 速通 https://github.com/limouren2000/llms-dev-study

## 六、当前坐标

- **阶段**：① Python 基础 · W1（第 3 个学习日）
- **已完成**：环境（uv/git/VS Code）→ `chat_cli_reference.py` 参考实现待用 → `contacts.py`：`add`/`list`/`quit` 存盘 已通，已推 GitHub
- **进行中**：`find`（关键字查询）
- **本阶段结束要能**：不看代码讲清下面这 5 行在干嘛

```python
if line.startswith("add "):
    parts = line.split()
    if len(parts) != 3:
        print("格式: add 姓名 电话")
        continue
    contacts.append({"name": parts[1], "phone": parts[2]})
```
