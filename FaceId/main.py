"""
main.py
-------
FacePass AiService — FastAPI application entry point.

Endpoints
~~~~~~~~~
  GET  /health                      — liveness probe
  GET  /info                        — service metadata
  POST /enroll/{student_id}         — save a new face embedding
  GET  /students/{student_id}/embeddings — list stored embeddings
  DEL  /students/{student_id}       — delete all embeddings for a student
  WS   /ws                          — real-time face analysis stream
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.websocket import init_pipeline, manager, ws_handler
from configs.logging_config import setup_logging
from configs.settings import settings
from storage.database import check_db_connection
from storage.repositories import EmbeddingRepository
from storage.vector_search import cosine_search

# Set up logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle manager."""
    logger.info("FacePass AiService starting up …")
    init_pipeline()           # load YOLO + ArcFace models eagerly
    logger.info("Startup complete — %d WebSocket connections active", manager.active_count)
    yield
    logger.info("FacePass AiService shutting down")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="FacePass AiService",
    description="Real-time face recognition and behaviour analysis.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REST endpoints ────────────────────────────────────────────────────────────

@app.get("/health", summary="Liveness probe")
async def health() -> dict[str, Any]:
    """Return service health status including database connectivity."""
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "connected" if db_ok else "unreachable",
        "active_streams": manager.active_count,
    }


@app.get("/info", summary="Service metadata")
async def info() -> dict[str, str]:
    """Return service version and configuration summary."""
    return {
        "service": "FacePass AiService",
        "version": "1.0.0",
        "model_version": settings.model_version,
        "device": settings.device,
    }


@app.post("/enroll/{student_id}", summary="Enrol a student face embedding")
async def enroll(student_id: int, embedding: list[float]) -> dict[str, Any]:

    if len(embedding) != 512:
        raise HTTPException(status_code=422, detail="Embedding must have exactly 512 elements")

    try:
        saved_id = EmbeddingRepository.save(
            student_id,
            np.array(embedding, dtype=np.float32)
        )

        # 🔥 Automatically reload pipeline state
        from app.websocket import get_pipeline
        pipeline = get_pipeline()
        pipeline.reload_state()

        logger.info("Embedding saved and pipeline reloaded automatically")

        return {
            "status": "saved",
            "id": saved_id,
            "student_id": student_id,
            "pipeline_reloaded": True
        }

    except Exception as exc:
        logger.error("Failed to enrol student_id=%d: %s", student_id, exc)
        raise HTTPException(status_code=500, detail="Failed to save embedding") from exc


@app.post("/recognize", summary="Recognize a face embedding")
async def recognize(embedding: list[float]):
    """
    Compare a 512-D embedding against stored embeddings
    and return the closest match.
    """

    if len(embedding) != 512:
        raise HTTPException(
            status_code=422,
            detail="Embedding must have exactly 512 elements",
        )

    try:
        result = cosine_search(np.array(embedding, dtype=np.float32))

        if result is None:
            return {
                "match": False,
                "student_id": None,
                "distance": None,
            }

        # you can adjust threshold later
        threshold = settings.sim_threshold

        if result.d <= threshold:
            return {
                "match": True,
                "student_id": result.student_id,
                "distance": result.d,
            }

        return {
            "match": False,
            "student_id": None,
            "distance": result.d,
        }

    except Exception as exc:
        logger.error("Recognition failed: %s", exc)
        raise HTTPException(status_code=500, detail="Recognition failed")


@app.get("/students/{student_id}/embeddings")
async def list_embeddings(student_id: int):
    records = EmbeddingRepository.get_by_student(student_id)

    return {
        "student_id": student_id,
        "count": len(records),
        "ids": [r["face_id"] for r in records],
    }


@app.delete("/students/{student_id}", summary="Delete all embeddings for a student")
async def delete_student(student_id: int) -> dict[str, Any]:
    """Remove all face embeddings for *student_id* from the database."""
    count = EmbeddingRepository.delete_by_student(student_id)
    return {"student_id": student_id, "deleted": count}


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def ws(ws: WebSocket) -> None:
    """Real-time face recognition and behaviour analysis stream."""
    await ws_handler(ws)

@app.post("/reload-embeddings")
async def reload_embeddings():
    """
    Reset pipeline runtime state without restarting server.
    """
    from app.websocket import get_pipeline

    pipeline = get_pipeline()
    pipeline.reload_state()

    return {"status": "pipeline reset"}