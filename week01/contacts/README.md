# contacts · 分层版通讯录

运行：`uv run python week01/contacts/cli.py`（在仓库根目录执行；直接跑脚本时该目录自动在 import 路径上）

命令：
- `add <姓名> <电话>` 添加联系人
- `list` 列出全部（带序号）
- `find <关键字>` 按姓名子串查找
- `del <用户号>` 按序号删除
- `quit` 退出并保存

存盘：`quit` 和意外退出（输入结束 / `EOFError`/ Ctrl+C 中断也会保存）都会保存，其余操作不落盘。

数据损坏：`contacts.json` 结构不对时提示「数据文件损坏，请检查 contacts.json」，不会覆盖原文件。

分层：`storage.py` 只管读写 json · `core.py` 只管业务逻辑 · `cli.py` 只管输入输出

测试：`uv run python week01/contacts/test_contacts.py`
