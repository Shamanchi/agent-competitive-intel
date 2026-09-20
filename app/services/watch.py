"""Хранилище baseline по конкурентам (in-memory, офлайн)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Snapshot(BaseModel):
    competitor: str
    price: float = Field(ge=0)
    features: list[str] = Field(default_factory=list)
    news_count: int = Field(ge=0)


class WatchStore:
    """Фиксирует baseline и историю последних изменений."""

    def __init__(self) -> None:
        self._baselines: dict[str, Snapshot] = {}
        self._last_changes: dict[str, list[dict]] = {}
        self._names: dict[str, str] = {}

    def watch(self, snapshot: Snapshot) -> Snapshot:
        key = snapshot.competitor.strip().lower()
        if not key:
            raise ValueError("competitor must not be empty")
        stored = Snapshot(
            competitor=snapshot.competitor.strip(),
            price=snapshot.price,
            features=sorted({f.strip().lower() for f in snapshot.features if f.strip()}),
            news_count=snapshot.news_count,
        )
        self._baselines[key] = stored
        self._names[key] = stored.competitor
        self._last_changes.pop(key, None)
        return stored

    def baseline(self, competitor: str) -> Snapshot | None:
        return self._baselines.get(competitor.strip().lower())

    def competitors(self) -> list[str]:
        return sorted(s.competitor for s in self._baselines.values())

    def record_changes(self, competitor: str, changes: list[dict]) -> None:
        key = competitor.strip().lower()
        self._names.setdefault(key, competitor.strip())
        self._last_changes[key] = changes

    def last_changes(self) -> dict[str, list[dict]]:
        return {self._names.get(key, key): changes for key, changes in self._last_changes.items()}

    def clear(self) -> None:
        self._baselines.clear()
        self._last_changes.clear()
        self._names.clear()


_store: WatchStore | None = None


def get_store() -> WatchStore:
    global _store
    if _store is None:
        _store = WatchStore()
    return _store
