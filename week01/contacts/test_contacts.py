from core import add_contact, delete_contact, find_contacts


def make_contacts():
    contacts = []
    for name in ["甲1", "甲2", "甲3", "乙1", "乙2", "乙3"]:
        add_contact(contacts, name, "111")
    return contacts


def test_add_contact():
    assert len(make_contacts()) == 6


def test_find_contacts():
    contacts = make_contacts()
    # 命中
    assert len(find_contacts(contacts, "甲")) == 3
    # 未命中
    assert find_contacts(contacts, "张") == []


def test_delete_contact():
    contacts = make_contacts()
    assert delete_contact(contacts, 1) == {"name": "甲1", "phone": "111"}
    assert len(contacts) == 5
    assert delete_contact(contacts, 5) == {"name": "乙3", "phone": "111"}
    assert delete_contact(contacts, 6) is None
    assert delete_contact(contacts, 0) is None
    assert delete_contact(contacts, -1) is None
