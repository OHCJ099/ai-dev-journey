import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "contacts.json"

def load_contacts(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return json.loads(text)

def save_contacts(path: Path, contacts: list[dict[str, str]]) -> None:
    path.write_text(json.dumps(contacts, ensure_ascii=False, indent=2), encoding="utf-8")
