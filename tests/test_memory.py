from holiday_management.memory import holiday_memory


def test_recall_degrades_gracefully(monkeypatch):
    """If the mem0 backend is unavailable, recall returns [] instead of raising."""
    def boom():
        raise RuntimeError("backend down")

    monkeypatch.setattr(holiday_memory, "_get_memory", boom)
    assert holiday_memory.recall_preferences("guest", "paris") == []


def test_remember_degrades_gracefully(monkeypatch):
    def boom():
        raise RuntimeError("backend down")

    monkeypatch.setattr(holiday_memory, "_get_memory", boom)
    # should not raise
    holiday_memory.remember_preferences("guest", "likes art")


def test_recall_parses_dict_results(monkeypatch):
    class FakeMemory:
        def search(self, query, filters=None):
            return {"results": [{"memory": "prefers boutique hotels"}]}

    monkeypatch.setattr(holiday_memory, "_get_memory", lambda: FakeMemory())
    assert holiday_memory.recall_preferences("guest", "hotels") == [
        "prefers boutique hotels"
    ]


def test_recall_respects_limit(monkeypatch):
    class FakeMemory:
        def search(self, query, filters=None):
            return {"results": [{"memory": f"pref {i}"} for i in range(10)]}

    monkeypatch.setattr(holiday_memory, "_get_memory", lambda: FakeMemory())
    assert len(holiday_memory.recall_preferences("guest", "x", limit=3)) == 3
