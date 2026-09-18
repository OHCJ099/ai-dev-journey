# contacts · 分层版通讯录

运行：`uv run python week01/contacts/cli.py`（在仓库根目录执行；直接跑脚本时该目录自动在 import 路径上）

命令：`add <姓名> <电话>` / `list` / `find <关键字>` / `del <用户号>` / `quit`（quit 时存盘）

分层：`storage.py` 只管读写 json · `core.py` 只管业务逻辑 · `cli.py` 只管输入输出
