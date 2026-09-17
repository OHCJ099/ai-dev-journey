import json
from pathlib import Path

# 文件读取
DATA_FILE = Path(__file__).parent / "contacts.json"
if DATA_FILE.exists():
    contacts = json.loads(DATA_FILE.read_text(encoding="utf-8"))
else:
    contacts = []

# 主循环
while True:
    line = input("> ")

    # add分支
    if line.startswith("add "):
        parts = line.split()
        if len(parts) != 3:
            print("格式: add 姓名 电话")
            continue
        contacts.append({"name": parts[1], "phone": parts[2]})   # ← append 归位到 add 分支内

    # delete分支
    elif line.startswith("del "):
        parts = line.split()
        if len(parts) != 2:
            print("格式: del 序号")
            continue

        try:
            del_index = int(parts[1])
        except ValueError:
            print("请输入数字")
            continue

        if len(contacts) >= del_index >= 1:
            del_user = contacts.pop(del_index - 1)
            print(f"已删除 {del_user['name']} {del_user['phone']}")
        else:
            print("数字不合法")    

    # list分支
    elif line == "list":
        for index, contact in enumerate(contacts, start = 1):
            print(f"{index}. {contact['name']} {contact['phone']}")
          
    # find分支     
    elif line.startswith("find "):
        found = False
        parts = line.split()
        if len(parts) != 2:
            print("格式: find 姓名")
            continue

        name = parts[1]
        for index, contact in enumerate(contacts, start = 1):
            if name in contact["name"]:
                print(f"{index}. {contact['name']} {contact['phone']}")
                found = True
        if not found:
            print(f"没找到{name}")

    # quit分支
    elif line == "quit":
        DATA_FILE.write_text(json.dumps(contacts, ensure_ascii=False, indent=2), encoding="utf-8")
        break

    else:
        print("unknown command")