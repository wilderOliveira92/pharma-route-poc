import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import medicos, rotas


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all tables on startup."""
    import models  # noqa: F401 — ensures models register with Base.metadata
    Base.metadata.create_all(bind=engine)
    yield


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Pharma Route POC",
    description="API de otimização de rotas para representantes farmacêuticos.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — origins from env var (comma-separated), fallback to Vite dev server
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
_allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(medicos.router)
app.include_router(rotas.router)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------


@app.get("/")
def raiz() -> dict:
    return {"status": "ok", "docs": "/docs"}
