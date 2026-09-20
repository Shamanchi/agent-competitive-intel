"""Сравнение снапшотов с baseline и сборка дайджеста."""

from __future__ import annotations

from app.services.watch import Snapshot


def diff_snapshots(
    baseline: Snapshot,
    current: Snapshot,
    price_alert_pct: float = 5.0,
    news_spike_mult: float = 2.0,
) -> list[dict]:
    """Вернуть список изменений. Детерминировано."""
    changes: list[dict] = []
    if baseline.price > 0:
        pct = round((current.price - baseline.price) / baseline.price * 100, 1)
        if abs(pct) >= price_alert_pct:
            kind = "price_drop" if pct < 0 else "price_hike"
            changes.append({"kind": kind, "detail": f"{baseline.price:g} -> {current.price:g} ({pct:+}%)"})
    old_features = set(baseline.features)
    new_features = {f.strip().lower() for f in current.features if f.strip()}
    for feature in sorted(new_features - old_features):
        changes.append({"kind": "feature_added", "detail": feature})
    for feature in sorted(old_features - new_features):
        changes.append({"kind": "feature_removed", "detail": feature})
    if baseline.news_count > 0 and current.news_count >= baseline.news_count * news_spike_mult:
        changes.append(
            {"kind": "news_spike", "detail": f"{baseline.news_count} -> {current.news_count} mentions"}
        )
    elif baseline.news_count == 0 and current.news_count > 0:
        changes.append({"kind": "news_spike", "detail": f"0 -> {current.news_count} mentions"})
    return changes


def build_digest(last_changes: dict[str, list[dict]]) -> str:
    """Собрать markdown-дайджест последних изменений."""
    if not last_changes:
        return "# Competitive digest\n\nNo changes recorded yet.\n"
    lines = ["# Competitive digest", ""]
    for competitor in sorted(last_changes):
        lines.append(f"## {competitor}")
        changes = last_changes[competitor]
        if not changes:
            lines.append("- No changes vs baseline.")
        for change in changes:
            lines.append(f"- {change['kind']}: {change['detail']}")
        lines.append("")
    return "\n".join(lines)
