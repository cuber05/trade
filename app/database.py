"""
CryptoTerminal — SQLite Database Layer
Handles portfolio holdings, watchlist, and alerts persistence.
"""

from __future__ import annotations

import json
import aiosqlite
from pathlib import Path
from typing import Optional

from app.config import get_settings


async def get_db() -> aiosqlite.Connection:
    """Get a database connection."""
    settings = get_settings()
    db = await aiosqlite.connect(str(settings.db_path))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db() -> None:
    """Create tables if they don't exist."""
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS portfolio_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                buy_price REAL NOT NULL,
                buy_date TEXT NOT NULL DEFAULT (datetime('now')),
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL UNIQUE,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                image_url TEXT DEFAULT '',
                added_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                condition TEXT NOT NULL,
                threshold REAL NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                is_triggered INTEGER NOT NULL DEFAULT 0,
                triggered_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                notes TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER,
                coin_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                triggered_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_holdings_coin ON portfolio_holdings(coin_id);
            CREATE INDEX IF NOT EXISTS idx_alerts_coin ON alerts(coin_id);
            CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active);
        """)
        await db.commit()
    finally:
        await db.close()


# ── Portfolio CRUD ──

async def get_all_holdings() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM portfolio_holdings ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def add_holding(data: dict) -> dict:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO portfolio_holdings (coin_id, symbol, name, amount, buy_price, buy_date, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data["coin_id"], data["symbol"], data["name"],
             data["amount"], data["buy_price"],
             data.get("buy_date", ""), data.get("notes", ""))
        )
        await db.commit()
        row_id = cursor.lastrowid
        cursor = await db.execute(
            "SELECT * FROM portfolio_holdings WHERE id = ?", (row_id,)
        )
        row = await cursor.fetchone()
        return dict(row)
    finally:
        await db.close()


async def update_holding(holding_id: int, data: dict) -> Optional[dict]:
    db = await get_db()
    try:
        fields = []
        values = []
        for key in ("amount", "buy_price", "buy_date", "notes"):
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        if not fields:
            return None
        fields.append("updated_at = datetime('now')")
        values.append(holding_id)
        await db.execute(
            f"UPDATE portfolio_holdings SET {', '.join(fields)} WHERE id = ?",
            values
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM portfolio_holdings WHERE id = ?", (holding_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def delete_holding(holding_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "DELETE FROM portfolio_holdings WHERE id = ?", (holding_id,)
        )
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


# ── Watchlist CRUD ──

async def get_watchlist() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM watchlist ORDER BY added_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def add_to_watchlist(data: dict) -> Optional[dict]:
    db = await get_db()
    try:
        await db.execute(
            """INSERT OR IGNORE INTO watchlist (coin_id, symbol, name, image_url)
               VALUES (?, ?, ?, ?)""",
            (data["coin_id"], data["symbol"], data["name"], data.get("image_url", ""))
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM watchlist WHERE coin_id = ?", (data["coin_id"],)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def remove_from_watchlist(coin_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute(
            "DELETE FROM watchlist WHERE coin_id = ?", (coin_id,)
        )
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


# ── Alerts CRUD ──

async def get_all_alerts(active_only: bool = False) -> list[dict]:
    db = await get_db()
    try:
        query = "SELECT * FROM alerts"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        cursor = await db.execute(query)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def create_alert(data: dict) -> dict:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO alerts (coin_id, symbol, name, alert_type, condition, threshold, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data["coin_id"], data["symbol"], data["name"],
             data["alert_type"], data["condition"],
             data["threshold"], data.get("notes", ""))
        )
        await db.commit()
        row_id = cursor.lastrowid
        cursor = await db.execute("SELECT * FROM alerts WHERE id = ?", (row_id,))
        row = await cursor.fetchone()
        return dict(row)
    finally:
        await db.close()


async def delete_alert(alert_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


async def toggle_alert(alert_id: int) -> Optional[dict]:
    db = await get_db()
    try:
        await db.execute(
            "UPDATE alerts SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (alert_id,)
        )
        await db.commit()
        cursor = await db.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def get_alert_history(limit: int = 50) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM alert_history ORDER BY triggered_at DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def add_alert_history(data: dict) -> None:
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO alert_history (alert_id, coin_id, symbol, alert_type, message)
               VALUES (?, ?, ?, ?, ?)""",
            (data.get("alert_id"), data["coin_id"], data["symbol"],
             data["alert_type"], data["message"])
        )
        await db.commit()
    finally:
        await db.close()
