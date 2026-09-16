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