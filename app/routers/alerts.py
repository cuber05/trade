"""
CryptoTerminal — Alert Routes
CRUD for price/volume/market alerts with history tracking.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from app import database as db

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


# ── Schemas ──

class AlertCreate(BaseModel):
    coin_id: str
    symbol: str
    name: str
    alert_type: str  # "price_above", "price_below", "volume_spike", "pct_change", "fear_greed"
    condition: str   # "above", "below", "crosses"
    threshold: float
    notes: str = ""


# ── Routes ──

@router.get("")
async def list_alerts(active_only: bool = Query(default=False)):
    """Get all alerts, optionally filtered to active only."""
    alerts = await db.get_all_alerts(active_only=active_only)
    return alerts


@router.post("")
async def create_alert(alert: AlertCreate):
    """Create a new alert."""
    result = await db.create_alert(alert.model_dump())
    return result


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    """Delete an alert."""
    success = await db.delete_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"success": True}


@router.put("/{alert_id}/toggle")
async def toggle_alert(alert_id: int):
    """Toggle an alert on/off."""
    result = await db.toggle_alert(alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


@router.get("/history")
async def alert_history(limit: int = Query(default=50, le=200)):
    """Get alert trigger history."""
    history = await db.get_alert_history(limit=limit)
    return history
