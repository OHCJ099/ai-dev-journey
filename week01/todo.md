# 本周待办清单（唯一权威版，不用记编号）

我（AI 教练）说的「Day 1 / Day 2」= 计划里的第几个学习日，**不是星期几**。以后我尽量不说编号，直接说「下一步」。

## 已完成 ✅
- [x] 建仓库 `~/ai-dev-journey`，装了 uv / openai / python-dotenv / httpx
- [x] 推到 GitHub：https://github.com/OHCJ099/ai-dev-journey
- [x] `.gitignore` 里排除了 `.env`（API key 不会泄露）
- [x] 试建 `scratch/demo2`：`uv init` → `uv add rich` → `uv run` 跑通彩色 hello

## 下一步（现在做这个）⏳
- [ ] 写 `week01/contacts.py` 第一版：输入 `add 张三 138` 存进列表，输入 `list` 打印出来，输入 `quit` 退出
      - 标准：能看到自己加的那条数据就算过
      - 不许复制粘贴，照着敲

## 之后（本周内，做完一件再说下一件）
- [ ] 通讯录能存到文件里（关掉再打开数据还在）→ 用 json
- [ ] 把通讯录拆成几个文件（storage / core / cli），函数加类型标注
- [ ] 学 `.env`：把 API key 从代码里挪出去
- [ ] 申请 DeepSeek API key，充值 10 元
- [ ] 写 `hello_api.py`：第一次调用大模型，打印回复和 token 消耗
- [ ] 改成流式输出（一个字一个字蹦出来）
- [ ] 做 `chat_cli` v0.1：命令行多轮对话，支持 /clear、/system、/save
- [ ] 推 GitHub + 写 README + 给我 3 句话周报

## 我卡住时的做法
1. 贴报错最后 5 行 + 说明你想要的结果
2. 卡超过 40 分钟就问我，别硬扛（但先自己查 15 分钟文档）
