"""
ai/pipeline.py
--------------
Central AI pipeline for FacePass.

Chains: Detection → Tracking → Recognition → Behaviour Analysis.

Each stage is timed and logged individually so bottlenecks can be
identified in production logs.
"""

import logging
import time
from typing import Any
import requests
import numpy as np

from ai.detector.yolo_face import YOLOFaceDetector
from ai.recognizer.arcface import ArcFaceRecognizer
from ai.recognizer.embedding_cache import EmbeddingCache
from ai.tracker.bot_sort import BoTSORT
from behavior.engagement import compute_engagement
from behavior.head_pose import estimate_pose
from configs.settings import settings
from storage.vector_search import cosine_search

logger = logging.getLogger(__name__)


class FacePipeline:
    """End-to-end face recognition and behaviour analysis pipeline.

    Typical usage::

        pipeline = FacePipeline()
        results = pipeline.process(frame)

    Each element of *results* is a dict with keys:
      - ``track_id``   – stable integer track identifier
      - ``bbox``       – ``[x1, y1, x2, y2]`` in pixel coordinates
      - ``student_id`` – matched student ID string, or ``None``
      - ``confidence`` – cosine similarity score (0–1), or ``None``
      - ``pitch``      – head pitch angle in degrees
      - ``yaw``        – head yaw angle in degrees
      - ``roll``       – head roll angle in degrees
      - ``engagement`` – ``"high"`` | ``"medium"`` | ``"low"``
    """

    def __init__(self) -> None:
        logger.info("Initialising FacePipeline …")
        self.detector = YOLOFaceDetector()
        self.tracker = BoTSORT()
        self.recognizer = ArcFaceRecognizer()
        self.cache = EmbeddingCache()
        self.frame_id: int = 0
        self.marked_attendance = set() # prevent duplicate attendance
        self.track_history = {}
        logger.info("FacePipeline ready")

    def reload_state(self):
            """
            Reset runtime state without restarting server.
            Useful after enrolling new students.
            """
            logger.info("Reloading pipeline runtime state...")
            # Clear attendance protection
            self.marked_attendance.clear()
            # Clear confidence smoothing history
            self.track_history.clear()
            # Reset tracker
            self.tracker = BoTSORT()
            logger.info("Pipeline state reset complete")

    # ── Main entry point ─────────────────────────────────────────────────────

    def process(self, frame: np.ndarray, session_id: str = "") -> list[dict[str, Any]]:
        """Process one video frame through the full pipeline.

        Args:
            frame:      BGR numpy array (H × W × 3).
            session_id: Optional correlation ID logged with every entry.

        Returns:
            List of per-face result dicts (see class docstring).
        """
        self.frame_id += 1
        t_total = time.perf_counter()
        log_prefix = f"[frame={self.frame_id}]"
        if session_id:
            log_prefix = f"[session={session_id}][frame={self.frame_id}]"

        try:
            # ── Stage 1: Detection ──────────────────────────────────────────
            t0 = time.perf_counter()
            detections = self.detector.detect(frame)
            t_detect = time.perf_counter() - t0

            # ── Stage 2: Tracking ───────────────────────────────────────────
            t0 = time.perf_counter()
            tracks = self.tracker.update(detections)
            t_track = time.perf_counter() - t0

            output: list[dict[str, Any]] = []

            t_recog = 0.0
            t_behav = 0.0

            for t in tracks:
                x1, y1, x2, y2 = [int(v) for v in t.bbox]

                if not hasattr(t, "last_seen_frame"):
                    t.last_seen_frame = self.frame_id
                else:
                    t.last_seen_frame = self.frame_id
                # Guard against degenerate boxes
                if x2 <= x1 or y2 <= y1:
                    logger.debug("%s Skipping degenerate bbox for track %d", log_prefix, t.track_id)
                    continue

                pad = 30  # add margin around face

                h, w, _ = frame.shape

                x1p = max(0, x1 - pad)
                y1p = max(0, y1 - pad)
                x2p = min(w, x2 + pad)
                y2p = min(h, y2 + pad)

                face_crop = frame[y1p:y2p, x1p:x2p]

                # ── Stage 3: Recognition (every EMBED_INTERVAL frames) ──────
                t0 = time.perf_counter()
                t_recog = 0.0

                if self.frame_id - t.last_embed_frame >= settings.embed_interval:
                    emb = self.recognizer.embed(face_crop)
                    if emb is not None:
                        self.cache.set(t.track_id, emb)
                        t.embedding = emb
                        t.last_embed_frame = self.frame_id

                    t_recog = time.perf_counter() - t0

                # ── Stage 4: Identity matching ──────────────────────────────
                student_id = None
                confidence = None
                status = "unknown"

                if hasattr(t, "locked_id") and t.locked_id is not None:
                    # 🔥 Re-validate locked identity
                    if t.embedding is not None:
                        match = cosine_search(t.embedding)
                        if match is None or match.d > settings.sim_threshold:
                            logger.info(f"Unlocking track {t.track_id} due to similarity drop")
                            t.locked_id = None
                            t.locked_conf = None
                        else:
                            student_id = t.locked_id
                            confidence = t.locked_conf
                            status = "recognized"
                    else:
                        student_id = t.locked_id
                        confidence = t.locked_conf
                        status = "recognized"

                else:
                    if t.embedding is not None:
                        match = cosine_search(t.embedding)

                        if match is not None and match.d <= settings.sim_threshold:
                            student_id = match.student_id
                            raw_conf = 1.0 - float(match.d)

                            history = self.track_history.setdefault(t.track_id, [])
                            history.append(raw_conf)

                            if len(history) > 5:
                                history.pop(0)

                            confidence = round(sum(history) / len(history), 4)
                            status = "recognized"

                            t.locked_id = student_id
                            t.locked_conf = confidence

                            if student_id not in self.marked_attendance:
                                try:
                                    url = f"http://localhost:8080/attendance/auto/{student_id}"
                                    response = requests.post(url)

                                    if response.status_code == 200:
                                        logger.info(f"Attendance marked in DB for student {student_id}")
                                        self.marked_attendance.add(student_id)

                                    elif response.status_code == 409:
                                        logger.info(f"Attendance already marked for student {student_id}")
                                        self.marked_attendance.add(student_id)

                                    else:
                                        logger.warning(f"Spring response: {response.status_code} - {response.text}")

                                except Exception as e:
                                    logger.error(f"Error calling Spring attendance API: {e}")
                        else:
                            # 🔥 Log unknown only once per track
                            if not hasattr(t, "unknown_logged"):
                                logger.info(f"Unknown face detected (track {t.track_id})")
                                t.unknown_logged = True

                # ── Stage 5: Behaviour analysis ─────────────────────────────
                t0 = time.perf_counter()
                pitch, yaw, roll = estimate_pose(face_crop)
                engagement = compute_engagement(pitch, yaw)
                t_behav = time.perf_counter() - t0

                output.append(
                    {
                        "track_id": t.track_id,
                        "bbox": [x1, y1, x2, y2],
                        "student_id": student_id,
                        "confidence": confidence,
                        "status": status,
                        "pitch": round(pitch, 2),
                        "yaw": round(yaw, 2),
                        "roll": round(roll, 2),
                        "engagement": engagement,
                    }
                )
            for track_id in list(self.track_history.keys()):
                if all(t.track_id != track_id for t in tracks):
                    self.track_history.pop(track_id, None)

            elapsed = (time.perf_counter() - t_total) * 1000
            logger.debug(
                "%s faces=%d | detect=%.1fms track=%.1fms "
                "recog=%.1fms behav=%.1fms | total=%.1fms",
                log_prefix,
                len(output),
                t_detect * 1000,
                t_track * 1000,
                t_recog * 1000,
                t_behav * 1000,
                elapsed,
            )
            return output

        except Exception:
            logger.exception("%s Unhandled error during pipeline.process()", log_prefix)
            return []
