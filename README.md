# AI 应用开发 6 个月学习仓库

> 目标：6 个月内独立完成 2-3 个可演示的 AI 应用项目，具备投递「初级 AI 应用工程师」岗位的能力。
> 方向：**应用层**（API 调用 / Prompt / RAG / Agent / 轻量工程化），不做算法研究、不从零训练模型。
> 节奏：每周 15-20 小时（工作日 1.5-2h，周末 3-4h）。
> 起点：2026-09-15。

## 技术优先级（从高到低）
1. Python 基础与工程能力
2. 大模型 API 调用（DeepSeek / 通义千问）
3. Prompt 工程
4. **RAG（核心能力）**
5. Agent / LangGraph
6. 轻量工程化（FastAPI + 部署）

技术栈：Python · uv · LangChain / LangGraph · Chroma（入门） · openGauss DataVec（进阶可选） · FastAPI · DeepSeek / 通义 API

## 六个月路线与进度

| 月份 | 主题 | 阶段产出 | 状态 |
|---|---|---|---|
| 第 1 月 | Python 补齐 + 首次调用大模型 API + 简单 Prompt | `chat_cli` 命令行对话应用 | 进行中 |
| 第 2 月 | Prompt 进阶 + 简单聊天应用（Web） | `prompt-lab` + 带前端的聊天应用 | 未开始 |
| 第 3-4 月 | RAG 完整掌握 | **个人/企业知识库问答**（可接 openGauss DataVec） | 未开始 |
| 第 5 月 | Agent / 工具调用 / 记忆 / LangGraph | 多步骤自主执行 Agent | 未开始 |
| 第 6 月 | 工程化打磨 + 简历 + 面试 | 2-3 个项目上线可演示 + 简历 + 面经 | 未开始 |

## 周进度记录

| 周 | 日期 | 主题 | 本周产出 | 卡点 |
|---|---|---|---|---|
| W01 | 09-15 ~ 09-21 | Python 复习 + 环境 + 首次 API 调用 | `week01/chat_cli` v0.1 | - |

## 目录约定（每个项目都遵守）
```
project-name/
├── README.md          # 项目说明：做什么、怎么跑、截图、踩坑
├── pyproject.toml     # 依赖（uv 管理）
├── .env.example       # 环境变量模板（真 key 写 .env，永不提交）
├── .gitignore
└── src/               # 源码
```
README 必须包含：一句话定位 / 功能列表 / 运行步骤 / 技术栈 / 遇到的坑与解决。
