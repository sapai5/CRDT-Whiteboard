"""
auth-service/main.py
─────────────────────
Auth Service entrypoint. Mounts all routers and configures middleware.
"""

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth import router as auth_router

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger("auth-service")

app = FastAPI(
    title="Whiteboard — Auth Service",
    description="Issues and validates JWTs. Manages user accounts.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
#tables first
from app.db import init_db
@app.on_evemt("begin")
async def begin():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"service": "auth", "status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.service_port, reload=True)
