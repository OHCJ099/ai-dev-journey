import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "contacts.json"
if DATA_FILE.exists():
    contacts = json.loads(DATA_FILE.read_text(encoding="utf-8"))
else:
    contacts = []

while True:
    line = input("> ")
    if line == "quit":
        break
    if line.startswith("add "):
        parts = line.split()
        if len(parts) != 3:
            print("格式: add 姓名 电话")
            continue
    elif line == "list":
        print(contacts)