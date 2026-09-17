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
    # quit分支
    if line == "quit":
        DATA_FILE.write_text(json.dumps(contacts, ensure_ascii=False, indent=2), encoding="utf-8")
        break

    # add分支
    if line.startswith("add "):
        parts = line.split()
        if len(parts) != 3:
            print("格式: add 姓名 电话")
            continue
        contacts.append({"name": parts[1], "phone": parts[2]})   # ← append 归位到 add 分支内

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
    
    else:
        print("unknown command")