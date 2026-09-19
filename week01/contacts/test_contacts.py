from core import add_contact, delete_contact, find_contacts

# ---- add_contact ----
contacts = []                          # 自己造数据，绝不用真的 contacts.json
add_contact(contacts, "甲1", "111")
add_contact(contacts, "甲2", "111")
add_contact(contacts, "甲3", "111")
add_contact(contacts, "乙1", "111")
add_contact(contacts, "乙2", "111")
add_contact(contacts, "乙3", "111")
assert len(contacts) == 6

# ---- find_contacts 命中 ----
assert len(find_contacts(contacts, "甲")) == 3

# ---- find_contacts 未命中 ----
assert find_contacts(contacts, "张") == []

# ---- delete_contact ----
assert(delete_contact(contacts, 1)) == ({"name": "甲1", "phone": "111"})
assert len(contacts) == 5
assert(delete_contact(contacts, 5)) == ({"name": "乙3", "phone": "111"})
assert(delete_contact(contacts, 6)) is None
assert(delete_contact(contacts, 0)) is None
assert(delete_contact(contacts, -1)) is None

print("ALL TESTS PASSED")
