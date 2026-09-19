import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "contacts.json"

# 读取文件
def load_contacts(path: Path) -> list[dict[str, str]]:
    # 正常情况: 不存在则返回空列表
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)

    # 异常情况：不能用return，否则返回给cli时以为是对的，后续又报错，这里直接raise
    # 多重判断由大到小
    if not isinstance(data, list):
        raise ValueError("读取的不是列表！") # 为什么不用TypeError?因为 Cli 接不住这个TypeError，他们父子不同级 # noqa: TRY004 —— 这不是参数校验，是文件内容校验；三种错要抛同一种
    for c in data:
        if not isinstance(c, dict):
            raise ValueError("列表内的值不是字典！") # noqa: TRY004 —— 这不是参数校验，是文件内容校验；三种错要抛同一种
        elif "name" not in c or "phone" not in c:
            raise ValueError("字典内的键缺失！")
    return data

# 保存文件
def save_contacts(path: Path, contacts: list[dict[str, str]]) -> None:
    path.write_text(json.dumps(contacts, ensure_ascii=False, indent=2), encoding="utf-8")