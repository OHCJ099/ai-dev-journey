from core import add_contact, delete_contact, find_contacts, list_contacts
from storage import DATA_FILE, load_contacts, save_contacts


def main() -> None:
    try:
        contacts = load_contacts(DATA_FILE)
    except ValueError:
        print("数据文件损坏，请检查 contacts.json")
        return

    # 主循环
    while True:
        try:
            line = input("> ")
        except EOFError:
            print("...")
            save_contacts(DATA_FILE, contacts)
            return

        # add分支
        if line.startswith("add "):
            parts = line.split()
            if len(parts) != 3:
                print("格式: add 姓名 电话")
                continue
            add_contact(contacts, parts[1], parts[2])

        # del分支
        elif line.startswith("del "):
            parts = line.split()   # 仿 add：参数个数校验 → int() 转换（try/except ValueError 留在这层）
            if len(parts) != 2:
                print("格式: del 序号")
                continue
            try:
                delete_num = int(parts[1])
            except ValueError:
                print("请输入数字")
                continue
            deleted = delete_contact(contacts, delete_num)
            if deleted is None:
                print("数字不合法")
            else:
                print(f"已删除 {deleted["name"]} {deleted["phone"]}")
                
        # list分支
        elif line == "list":
            text = list_contacts(contacts) # 调 list_contacts → for 循环打印 f"{序号}. {姓名} {电话}"
            for index, contact in text:
                print(f"{index}. {contact["name"]} {contact["phone"]}")

        # find分支
        # 仿 add 校验参数 → 调 find_contacts → 结果为空就打印 f"没找到{关键字}"
        elif line.startswith("find "):
            parts = line.split()
            if len(parts) != 2:
                print("格式: find 姓名")
                continue
            text = find_contacts(contacts, parts[1])
            if not text:
                print(f"没找到{parts[1]}")
            for index, contact in text:
                print(f"{index}. {contact["name"]} {contact["phone"]}")

        # quit分支
        elif line == "quit":
            save_contacts(DATA_FILE, contacts)
            break
        else:
            print("unknown command")


if __name__ == "__main__":
    main()