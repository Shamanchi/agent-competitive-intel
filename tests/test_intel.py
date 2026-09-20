"""Unit-тесты диффа и дайджеста: без сети, детерминированы."""

from app.services.intel import build_digest, diff_snapshots
from app.services.watch import Snapshot, WatchStore


def _baseline() -> Snapshot:
    return Snapshot(competitor="Acme", price=99, features=["sso"], news_count=3)


def test_diff_detects_all_moves() -> None:
    current = Snapshot(competitor="Acme", price=79, features=["sso", "audit-log"], news_count=9)
    changes = diff_snapshots(_baseline(), current)
    kinds = {change["kind"] for change in changes}
    assert kinds == {"price_drop", "feature_added", "news_spike"}


def test_diff_quiet_when_nothing_changed() -> None:
    changes = diff_snapshots(_baseline(), _baseline())
    assert changes == []


def test_diff_below_threshold_silent() -> None:
    current = Snapshot(competitor="Acme", price=98, features=["sso"], news_count=3)
    changes = diff_snapshots(_baseline(), current, price_alert_pct=5.0)
    assert all(change["kind"] != "price_drop" for change in changes)


def test_store_watch_and_competitors() -> None:
    store = WatchStore()
    store.watch(_baseline())
    assert store.competitors() == ["Acme"]
    store.record_changes("Acme", [{"kind": "price_drop", "detail": "x"}])
    digest = build_digest(store.last_changes())
    assert "## Acme" in digest
    assert "price_drop" in digest


def test_empty_digest() -> None:
    assert "No changes" in build_digest({})
