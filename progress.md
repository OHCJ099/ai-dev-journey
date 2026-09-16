# 进度台账

> 规则：**每个学习日结束，子教练在这里追加一行**。总指挥官按这张表验收。
> 写法要求：产出必须是可核对的东西（文件名 / commit hash / 链接），不许写「学习了 xxx」。

| 日期 | 阶段 | 产出（文件/commit） | 讲回情况 | 卡点 | 备注 |
|---|---|---|---|---|---|
| 2026-09-15 | ① 环境 | `.gitignore`+仓库初始化，commit `871b141`，GitHub `OHCJ099/ai-dev-journey` | — | PowerShell 不认 `ls -a`（bash 语法） | 项目与 Hermes 家目录搬到 D 盘 |
| 2026-09-16 | ① Python | `week01/contacts.py` v1：add/list + 参数校验，commit `1a4ce70` | ❌ 讲不出来 | 抄完不知道在干嘛 → 触发体系重做 | 已建立三步法与子教练体系 |
| 2026-09-16 | ① Python | json 持久化，commit `c506042`（含 `contacts.json`） | ✅ 已讲回（15:10 补做，5 行逐行讲通） | `append` 贴错分支（缩进=分支归属） | `find` 未完成 |
| 2026-09-16 | ① Python | `week01/contacts.py` find 分支：`startswith` + 参数校验 + 标记变量 + "没找到"提示 + 未知命令兜底，commit `dc0d00a`（已 push） | ✅ 讲回通过（31–41 行逐行讲对） | 两次"改了没存盘"；`found = False` 写在循环内 → 搜第一条会多打一行"没找到" | 学习期关掉 VS Code AI 补全（卸载 Qoder CN / TraeCode + 全局 settings）；序号与「find 李 包含匹配」顺延 Day3 |

## 待验收项（总指挥官关注）

- [x] 学员能否不看代码讲清 `add` 分支那 5 行（dict / split / len / continue / append）—— 09-16 15:45 通过
- [x] `find` 是否实现（含"没找到"提示）—— 09-16 16:15 总指挥亲自跑 `find 李四 / 王五 / 赵六`，各只输出一行，commit `dc0d00a`
- [ ] `del` 是否实现（含 ValueError / IndexError 兜底，`enumerate` 序号）
- [ ] `list` / `find` 是否带序号（`enumerate`，`del` 的前置条件）
- [ ] "改完先 `Ctrl+S` 存盘再运行"是否形成习惯（09-16 一天踩了两次）
