# core.py —— 只处理内存里的数据：增 / 列 / 查 / 删。
#            不读文件、不打印、不 input()，只跟 cli 交接。


def add_contact(contacts: list[dict[str, str]], name: str, phone: str) -> None:
    contacts.append({"name": name, "phone": phone})


def list_contacts(contacts: list[dict[str, str]]) -> list[tuple[int, dict[str, str]]]:
    new_list = []
    # start=1：序号从 1 开始，是给用户看的（不是索引）
    for index, contact in enumerate(contacts, start=1):
        new_list.append((index, contact))
    return new_list


def find_contacts(
    contacts: list[dict[str, str]], keyword: str
) -> list[tuple[int, dict[str, str]]]:
    new_list = []
    for index, contact in enumerate(contacts, start=1):
        # in：是子串匹配，为了区分"name" in c，c是字典
        if keyword in contact["name"]:
            new_list.append((index, contact))
    return new_list


def delete_contact(
    contacts: list[dict[str, str]], user_no: int
) -> dict[str, str] | None:
    # len(contacts)：user_no收的是用户号与len对齐，处理索引时再user_no - 1
    if 1 <= user_no <= len(contacts):
        return contacts.pop(user_no - 1)
    return None
