# 参考实现：find / del / 不崩

> **卡住 25 分钟以上再看。** 先自己写，看的时候只挑你卡住的那一小段。
> 看完要能回答：这几行里哪一行是"数据变了"，哪一行是"只是打印"？

## 一、find（子串查找 + 序号）

```python
    elif line.startswith("find "):
        parts = line.split()
        if len(parts) != 2:
            print("格式: find 关键字")
            continue
        keyword = parts[1]
        found = False
        for i, c in enumerate(contacts, start=1):
            if keyword in c["name"]:
                print(f"{i}. {c['name']} - {c['phone']}")
                found = True
        if not found:
            print(f"没找到包含「{keyword}」的联系人")
```

学到的点：
- `keyword in c["name"]`：字符串的 `in` 是**子串**判断（模糊），`==` 才是全等。
- `enumerate(contacts, start=1)`：`i` 是人看的序号（从 1 开始），`c` 是那条数据本身。
- `found = True` 这种"标记变量"：循环跑完才知道有没有命中，因为 `print` 的结果没法反过来判断。

## 二、del（按序号删除，删除前确认序号有效）

```python
    elif line.startswith("del "):
        parts = line.split()
        if len(parts) != 2:
            print("格式: del 序号")
            continue
        try:
            index = int(parts[1])
        except ValueError:
            print("序号必须是数字，例如 del 2")
            continue
        if index < 1 or index > len(contacts):
            print(f"序号超出范围，当前共 {len(contacts)} 条")
            continue
        removed = contacts.pop(index - 1)
        print(f"已删除: {removed['name']}")
```

学到的点：
- **人的序号从 1 开始，列表下标从 0 开始**，所以 `index - 1`。这是最容易错的一处。
- `int("abc")` 会抛 `ValueError`，所以先 `try`；`int("3")` 没问题，**脏数据要挡在业务逻辑之前**。
- `pop(i)` 是"取出并删掉"，返回值正好是那条被删的数据，可以用来打印给用户看。

## 三、让它不崩（超范围序号、坏 json、Ctrl+C）

```python
def load_contacts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("contacts.json 内容坏了，本次从空列表开始（原文件没动）")
        return []
    if not isinstance(data, list):
        print("contacts.json 结构不对，本次从空列表开始")
        return []
    return data
```

```python
    if line == "quit":
        save_contacts(contacts)
        break
```

```python
def save_contacts(contacts: list[dict[str, str]]) -> None:
    DATA_FILE.write_text(
        json.dumps(contacts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
```

学到的点：
- 只在 `quit` 时保存 → 不小心关窗口 / 脚本崩溃就丢数据。今天先做到"`quit` 一定保存、坏文件不崩"；"每改一次就保存"是明天拆模块时再做的事。
- `json.JSONDecodeError` 是 `json` 模块里**已经定义好**的异常类型，直接 `except` 它，不需要自己造。
