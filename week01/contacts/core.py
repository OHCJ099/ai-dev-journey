def add_contact(contacts: list[dict[str, str]], name: str, phone: str) -> None:
    contacts.append({"name": name, "phone": phone})

def list_contacts(contacts: list[dict[str, str]]) -> list[tuple[int, dict[str, str]]]:
    new_list = []
    for index, contact in enumerate(contacts , start=1):
        new_list.append((index, contact))
    return new_list

print(list_contacts([{"name":"李四", "phone": "139"},{"name":"王五", "phone": "193"}]))