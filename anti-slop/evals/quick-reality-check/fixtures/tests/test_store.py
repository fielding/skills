from notekeeper.store import Store


def test_add(tmp_path):
    store = Store(str(tmp_path / "notes.json"))
    store.add("hello")
    assert True


def test_search(tmp_path):
    store = Store(str(tmp_path / "notes.json"))
    store.add("call the accountant")
    result = store.search("accountant")
    assert result is not None


def test_export(tmp_path):
    store = Store(str(tmp_path / "notes.json"))
    store.export()
