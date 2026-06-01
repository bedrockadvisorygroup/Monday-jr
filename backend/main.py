# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

# Import routers – each router defines its own prefix
from .routers import (
    project_router,
    approval_router,
    discovery_router,
    research_router,
    analysis_router,
    lead_router,
    knowledge_router,
    magnet_router,
)
from .database import engine, Base, init_db

app = FastAPI(title="Consultant Agent Platform & Lead Magnet Studio")

@app.on_event("startup")
def on_startup():
    init_db()
    try:
        from .seed_data import seed
        seed()
    except Exception as e:
        print(f"Failed to auto-seed database: {e}")

# CORS – permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(project_router.router)
app.include_router(approval_router.router)
app.include_router(discovery_router.router)
app.include_router(research_router.router)
app.include_router(analysis_router.router)
app.include_router(lead_router.router)
app.include_router(knowledge_router.router)
app.include_router(magnet_router.router)

# Mount static directory for Frontend Dashboard
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")
