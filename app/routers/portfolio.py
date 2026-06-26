"""
CryptoTerminal — Portfolio & Watchlist Routes
CRUD for holdings, watchlist items, and portfolio summary.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app import database as db
from app.services import coingecko

router = APIRouter(prefix="/api/v1", tags=["portfolio"])


# ── Schemas ──

class HoldingCreate(BaseModel):
    coin_id: str
    symbol: str
    name: str
    amount: float = Field(gt=0)
    buy_price: float = Field(gt=0)
    buy_date: str = ""
    notes: str = ""


class HoldingUpdate(BaseModel):
    amount: Optional[float] = None
    buy_price: Optional[float] = None
    buy_date: Optional[str] = None
    notes: Optional[str] = None


class WatchlistAdd(BaseModel):
    coin_id: str
    symbol: str
    name: str
    image_url: str = ""


# ── Portfolio Routes ──

@router.get("/portfolio")
async def get_portfolio():
    """Get all portfolio holdings with current prices."""
    holdings = await db.get_all_holdings()

    if not holdings:
        return {
            "holdings": [],
            "total_invested": 0,
            "total_value": 0,
            "total_pnl": 0,
            "total_pnl_pct": 0,
        }

    # Get current prices for all held coins
    coin_ids = list(set(h["coin_id"] for h in holdings))
    prices_data = await coingecko.get_simple_price(coin_ids)

    total_invested = 0
    total_value = 0

    for h in holdings:
        invested = h["amount"] * h["buy_price"]
        total_invested += invested

        current_price = 0
        change_24h = 0
        if prices_data and h["coin_id"] in prices_data:
            coin_price = prices_data[h["coin_id"]]
            current_price = coin_price.get("usd", 0) or 0
            change_24h = coin_price.get("usd_24h_change", 0) or 0

        current_value = h["amount"] * current_price
        total_value += current_value
        pnl = current_value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0

        h["current_price"] = current_price
        h["current_value"] = current_value
        h["invested"] = invested
        h["pnl"] = pnl
        h["pnl_pct"] = pnl_pct
        h["change_24h"] = change_24h

    total_pnl = total_value - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    return {
        "holdings": holdings,
        "total_invested": total_invested,
        "total_value": total_value,
        "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
    }


@router.post("/portfolio")
async def add_portfolio_holding(holding: HoldingCreate):
    """Add a new holding to the portfolio."""
    result = await db.add_holding(holding.model_dump())
    return result


@router.put("/portfolio/{holding_id}")
async def update_portfolio_holding(holding_id: int, holding: HoldingUpdate):
    """Update an existing holding."""
    update_data = {k: v for k, v in holding.model_dump().items() if v is not None}
    result = await db.update_holding(holding_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Holding not found")
    return result


@router.delete("/portfolio/{holding_id}")
async def delete_portfolio_holding(holding_id: int):
    """Delete a holding from the portfolio."""
    success = await db.delete_holding(holding_id)
    if not success:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {"success": True}


# ── Watchlist Routes ──

@router.get("/watchlist")
async def get_watchlist():
    """Get watchlist with current prices."""
    items = await db.get_watchlist()
    if not items:
        return []

    # Get current prices
    coin_ids = [item["coin_id"] for item in items]
    prices_data = await coingecko.get_simple_price(coin_ids)

    for item in items:
        if prices_data and item["coin_id"] in prices_data:
            coin_price = prices_data[item["coin_id"]]
            item["current_price"] = coin_price.get("usd", 0) or 0
            item["change_24h"] = coin_price.get("usd_24h_change", 0) or 0
            item["market_cap"] = coin_price.get("usd_market_cap", 0) or 0
            item["volume_24h"] = coin_price.get("usd_24h_vol", 0) or 0
        else:
            item["current_price"] = 0
            item["change_24h"] = 0
            item["market_cap"] = 0
            item["volume_24h"] = 0

    return items


@router.post("/watchlist")
async def add_watchlist_item(item: WatchlistAdd):
    """Add a coin to the watchlist."""
    result = await db.add_to_watchlist(item.model_dump())
    return result


@router.delete("/watchlist/{coin_id}")
async def remove_watchlist_item(coin_id: str):
    """Remove a coin from the watchlist."""
    success = await db.remove_from_watchlist(coin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Coin not in watchlist")
    return {"success": True}
