"""room-service/main.py — Room Service entrypoint."""

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.rooms import router as rooms_router

logging.basicConfig(level=settings.log_level.upper())

app = FastAPI(
    title="Whiteboard — Room Service",
    description="Manages rooms, participants, and issues WS join tickets.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms_router)


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"service": "room", "status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.service_port, reload=True)
