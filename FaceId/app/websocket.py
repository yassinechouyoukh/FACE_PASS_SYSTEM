"""
app/websocket.py
----------------
WebSocket handler for real-time face recognition and behaviour analysis.

Key design decisions
~~~~~~~~~~~~~~~~~~~~~
* ``pipeline.process()`` is CPU-bound (YOLO + InsightFace + MediaPipe).
  Running it directly on the async event loop would block all other
  connections.  We offload it to a **thread pool executor** so the
  event loop stays responsive.

* ``ConnectionManager`` keeps a registry of active connections so the
  server can broadcast to all streams or cleanly disconnect them on
  shutdown.

Scaling note
~~~~~~~~~~~~
At >50 concurrent streams, consider moving frame processing to
a Celery/Redis task queue:

    1. WebSocket handler pushes raw frame bytes to a Redis list.
    2. Celery workers (with GPU) pop frames and publish results to a
       Redis Pub/Sub channel keyed by session_id.
    3. A lightweight async consumer re-reads Redis and pushes JSON
       over the WebSocket.

This decouples ingestion from compute and allows horizontal scaling.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from fastapi import WebSocket, WebSocketDisconnect

from ai.pipeline import FacePipeline

logger = logging.getLogger(__name__)

# Shared thread pool — one thread per CPU core (frame processing is GIL-releasing
# during YOLO/InsightFace inference via native C extensions).
_executor = ThreadPoolExecutor(thread_name_prefix="pipeline")

# Module-level singleton pipeline — created once at startup via lifespan.
_pipeline: FacePipeline | None = None


def init_pipeline() -> None:
    """Initialise the module-level pipeline singleton.

    Called from the FastAPI lifespan so heavy model loading happens
    at startup, not on the first WebSocket connection.
    """
    global _pipeline
    if _pipeline is None:
        logger.info("Loading FacePipeline …")
        _pipeline = FacePipeline()


def get_pipeline() -> FacePipeline:
    """Return the shared pipeline, creating it if necessary."""
    global _pipeline
    if _pipeline is None:
        init_pipeline()
    return _pipeline  # type: ignore[return-value]


# ── Connection manager ────────────────────────────────────────────────────────

class ConnectionManager:
    """Track active WebSocket connections for lifecycle management."""

    def __init__(self) -> None:
        self._active: dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket) -> str:
        """Accept *ws* and register it; return a unique session ID."""
        await ws.accept()
        session_id = str(uuid.uuid4())[:8]
        self._active[session_id] = ws
        logger.info("WebSocket connected  session=%s  total=%d", session_id, len(self._active))
        return session_id

    def disconnect(self, session_id: str) -> None:
        """Remove a session from the registry."""
        self._active.pop(session_id, None)
        logger.info("WebSocket disconnected session=%s  total=%d", session_id, len(self._active))

    @property
    def active_count(self) -> int:
        return len(self._active)


manager = ConnectionManager()


# ── Handler ───────────────────────────────────────────────────────────────────

async def ws_handler(ws: WebSocket) -> None:
    """Handle a single WebSocket session.

    Protocol:
      Client → Server : raw JPEG/PNG frame as bytes
      Server → Client : JSON list of per-face result dicts

    The pipeline runs in a thread-pool executor so the event loop is
    never blocked by CPU-intensive inference.
    """
    session_id = await manager.connect(ws)
    pipeline = get_pipeline()
    loop = asyncio.get_event_loop()

    try:
        processing = False
        while True:
            data = await ws.receive_bytes()

            if processing:
                continue   # drop frame

            processing = True

            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                processing = False
                continue

            results = await loop.run_in_executor(
                _executor,
                pipeline.process,
                frame,
                session_id,
            )

            await ws.send_json(results)
            processing = False

    except WebSocketDisconnect:
        logger.info("session=%s WebSocket disconnected by client", session_id)
    except Exception:
        logger.exception("session=%s Unexpected error in ws_handler", session_id)
    finally:
        manager.disconnect(session_id)
