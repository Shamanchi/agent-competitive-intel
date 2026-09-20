"""Эндпоинты наблюдения, сравнения и дайджеста."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.intel import build_digest, diff_snapshots
from app.services.watch import Snapshot, WatchStore, get_store

router = APIRouter()


class SnapshotRequest(BaseModel):
    competitor: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0, le=1_000_000_000)
    features: list[str] = Field(default_factory=list, max_length=100)
    news_count: int = Field(default=0, ge=0)


class CheckResponse(BaseModel):
    competitor: str
    changes: list[dict]


def get_book() -> WatchStore:
    return get_store()


@router.post("/watch", response_model=Snapshot)
async def watch(request: SnapshotRequest, book: WatchStore = Depends(get_book)) -> Snapshot:
    try:
        return book.watch(Snapshot(**request.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/check", response_model=CheckResponse)
async def check(
    request: SnapshotRequest,
    book: WatchStore = Depends(get_book),
    settings: Settings = Depends(get_settings),
) -> CheckResponse:
    baseline = book.baseline(request.competitor)
    if baseline is None:
        raise HTTPException(status_code=404, detail=f"no baseline for {request.competitor}")
    current = Snapshot(**request.model_dump())
    changes = diff_snapshots(
        baseline,
        current,
        price_alert_pct=settings.price_alert_pct,
        news_spike_mult=settings.news_spike_mult,
    )
    book.record_changes(current.competitor, changes)
    return CheckResponse(competitor=current.competitor, changes=changes)


@router.get("/competitors")
async def competitors(book: WatchStore = Depends(get_book)) -> dict:
    return {"competitors": book.competitors()}


@router.get("/digest")
async def digest(book: WatchStore = Depends(get_book)) -> dict:
    return {"digest_md": build_digest(book.last_changes())}
