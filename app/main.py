"""
CryptoTerminal — FastAPI Application Entry Point
Serves the API + static frontend. Run with: uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, BASE_DIR
from app.database import init_db
from app.cache import cache
from app.routers import market, coins, portfolio, alerts, dex_defi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cryptoterminal")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("🚀 CryptoTerminal starting up...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    logger.info("✅ CryptoTerminal is ready!")
    yield

    # Cleanup
    await cache.clear()
    logger.info("👋 CryptoTerminal shut down.")


# ── Create App ──
app = FastAPI(
    title="CryptoTerminal",
    description="AI-Powered Bloomberg Terminal for Crypto Traders",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (allow frontend in development) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register API Routers ──
app.include_router(market.router)
app.include_router(coins.router)
app.include_router(portfolio.router)
app.include_router(alerts.router)
app.include_router(dex_defi.router)


# ── Health Check ──
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "cache_size": cache.size,
    }


# ── Static Files & SPA Routing ──
static_dir = BASE_DIR / "static"

if static_dir.exists():
    # Mount CSS and JS directories
    if (static_dir / "css").exists():
        app.mount("/css", StaticFiles(directory=str(static_dir / "css")), name="css")
    if (static_dir / "js").exists():
        app.mount("/js", StaticFiles(directory=str(static_dir / "js")), name="js")
    if (static_dir / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    @app.get("/")
    async def serve_index():
        """Serve the main SPA page."""
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return JSONResponse(
            {"message": "CryptoTerminal API is running. Frontend not found at /static/index.html"},
            status_code=200,
        )

    # Catch-all for SPA client-side routing (must be last)
    @app.get("/{full_path:path}")
    async def spa_catch_all(full_path: str):
        """Serve index.html for any non-API, non-static route (SPA support)."""
        # Don't catch API routes
        if full_path.startswith("api/"):
            return JSONResponse({"error": "Not found"}, status_code=404)

        # Check if it's an actual static file
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        # Otherwise serve the SPA
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return JSONResponse({"error": "Not found"}, status_code=404)
else:
    @app.get("/")
    async def api_root():
        return {
            "message": "CryptoTerminal API is running",
            "docs": "/docs",
            "health": "/api/health",
        }


# ── Error Handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
