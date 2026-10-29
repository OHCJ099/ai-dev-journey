from id_practice import build_ids


def test_build_ids_order():
    docs = [
        {"source": "A", "text": "x"},
        {"source": "B", "text": "y"},
        {"source": "A", "text": "z"},
    ]
    assert build_ids(docs) == ["A-1", "B-1", "A-2"]


def test_build_ids_empty():
    assert build_ids([]) == []
