# 进度台账

> 规则：**每个学习日结束，子教练在这里追加一行**。总指挥官按这张表验收。
> 写法要求：产出必须是可核对的东西（文件名 / commit hash / 链接），不许写「学习了 xxx」。

| 日期 | 阶段 | 产出（文件/commit） | 讲回情况 | 卡点 | 备注 |
|---|---|---|---|---|---|
| 2026-09-15 | ① 环境 | `.gitignore`+仓库初始化，commit `871b141`，GitHub `OHCJ099/ai-dev-journey` | — | PowerShell 不认 `ls -a`（bash 语法） | 项目与 Hermes 家目录搬到 D 盘 |
| 2026-09-16 | ① Python | `week01/contacts.py` v1：add/list + 参数校验，commit `1a4ce70` | ❌ 讲不出来 | 抄完不知道在干嘛 → 触发体系重做 | 已建立三步法与子教练体系 |
| 2026-09-16 | ① Python | json 持久化，commit `c506042`（含 `contacts.json`） | ⏳ 待讲回 | `append` 贴错分支（缩进=分支归属） | `find` 未完成 |

## 待验收项（总指挥官关注）

- [ ] 学员能否不看代码讲清 `add` 分支那 5 行（dict / split / len / continue / append）
- [ ] `find` 是否实现（含"没找到"提示）
- [ ] `del` 是否实现（含 ValueError / IndexError 兜底，`enumerate` 序号）
- [ ] 是否养成"能跑的版本先 commit 再改"的习惯
