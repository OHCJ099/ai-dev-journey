# core.py —— 只处理内存里的数据：增 / 列 / 查 / 删。
#            不读文件、不打印、不 input()，只跟 cli 交接。

def add_contact(contacts: list[dict[str, str]], name: str, phone: str) -> None:
    contacts.append({"name": name, "phone": phone})

def list_contacts(contacts: list[dict[str, str]]) -> list[tuple[int, dict[str, str]]]:
    new_list = []
    # start=1 -- 用户看：自己新开的列表，负责"给人看"
    for index, contact in enumerate(contacts ,start=1):
        new_list.append((index, contact))
    return new_list

def find_contacts(contacts: list[dict[str, str]], keyword: str) -> list[tuple[int, dict[str, str]]]:
    new_list = []
    for index, contact in enumerate(contacts, start=1):
        # in -- 子串匹配(区分"name" in c) c:列表
        if keyword in contact["name"]:
            new_list.append((index, contact))
    return new_list

def delete_contact(contacts: list[dict[str, str]], user_no: int) -> dict[str, str] | None:
    # len(contact)：user_no对齐视觉序号非索引，处理索引时user_no - 1
    if 1 <= user_no <= len(contacts):   
        return contacts.pop(user_no - 1)
    return None
