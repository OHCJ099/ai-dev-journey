def add_contact(contacts: list[dict[str, str]], name: str, phone: str) -> None:
    contacts.append({"name": name, "phone": phone})

def list_contacts(contacts: list[dict[str, str]]) -> list[tuple[int, dict[str, str]]]:
    new_list = []
    for index, contact in enumerate(contacts ,start=1):
        new_list.append((index, contact))
    return new_list

def find_contacts(contacts: list[dict[str, str]], keyword: str) -> list[tuple[int, dict[str, str]]]:
    new_list = []
    for index, contact in enumerate(contacts, start=1):
        if keyword in contact["name"]:
            new_list.append((index, contact))
    return new_list

def delete_contact(contacts: list[dict[str, str]], user_no: int) -> dict[str, str] | None:
    if 1 <= user_no <= len(contacts):
        return contacts.pop(user_no - 1)
    return None
