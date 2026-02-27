"""
behavior/head_pose.py
---------------------
Head pose estimation using MediaPipe FaceMesh.

Returns (pitch, yaw, roll) in degrees for the given face crop.
Falls back to a zero-tuple if MediaPipe is unavailable or no face
is detected (e.g., during unit tests with a blank image).
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

# Lazy-import MediaPipe so the rest of the project still imports cleanly
# even when mediapipe is not installed (useful in CI / unit tests).
try:
    import mediapipe as mp

    _mp_face_mesh = mp.solutions.face_mesh
    _MEDIAPIPE_AVAILABLE = True
except ImportError:
    _mp_face_mesh = None
    _MEDIAPIPE_AVAILABLE = False
    logger.warning("mediapipe not installed — head_pose will return zeros")

# ── Landmark indices (MediaPipe 468-point mesh) ─────────────────────────────
# Chin, nose tip, left/right eye corners, left/right mouth corners
_LANDMARK_IDS = [152, 1, 33, 263, 78, 308]

# Canonical 3-D reference points (metric, arbitrary scale)
_MODEL_POINTS = np.array(
    [
        [0.0, -330.0, -65.0],   # chin
        [0.0, 0.0, 0.0],        # nose tip
        [-225.0, 170.0, -135.0],# left eye, left corner
        [225.0, 170.0, -135.0], # right eye, right corner
        [-150.0, -150.0, -125.0],# left mouth corner
        [150.0, -150.0, -125.0], # right mouth corner
    ],
    dtype=np.float64,
)

_face_mesh_instance = None


def _get_face_mesh():
    """Return (and lazily create) a shared FaceMesh instance."""
    global _face_mesh_instance
    if _face_mesh_instance is None and _MEDIAPIPE_AVAILABLE:
        _face_mesh_instance = _mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
        )
    return _face_mesh_instance


def estimate_pose(face_crop: np.ndarray) -> tuple[float, float, float]:
    """Estimate head pose angles from a cropped face image.

    Uses a PnP solver on 6 facial landmarks extracted by MediaPipe.

    Args:
        face_crop: BGR numpy array of a cropped face region.

    Returns:
        ``(pitch, yaw, roll)`` in degrees.
        Returns ``(0.0, 0.0, 0.0)`` if estimation fails.
    """
    import cv2

    if face_crop is None or face_crop.size == 0 or not _MEDIAPIPE_AVAILABLE:
        return 0.0, 0.0, 0.0

    h, w = face_crop.shape[:2]
    rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
    mesh = _get_face_mesh()

    try:
        result = mesh.process(rgb)
        if not result.multi_face_landmarks:
            return 0.0, 0.0, 0.0

        landmarks = result.multi_face_landmarks[0].landmark
        img_points = np.array(
            [[landmarks[i].x * w, landmarks[i].y * h] for i in _LANDMARK_IDS],
            dtype=np.float64,
        )

        focal = w
        cam_matrix = np.array(
            [[focal, 0, w / 2], [0, focal, h / 2], [0, 0, 1]],
            dtype=np.float64,
        )
        dist_coeffs = np.zeros((4, 1))

        success, rvec, _ = cv2.solvePnP(
            _MODEL_POINTS, img_points, cam_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        if not success:
            return 0.0, 0.0, 0.0

        rmat, _ = cv2.Rodrigues(rvec)
        # Decompose rotation matrix → Euler angles
        sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
        singular = sy < 1e-6
        if not singular:
            pitch = float(np.degrees(np.arctan2(rmat[2, 1], rmat[2, 2])))
            yaw   = float(np.degrees(np.arctan2(-rmat[2, 0], sy)))
            roll  = float(np.degrees(np.arctan2(rmat[1, 0], rmat[0, 0])))
        else:
            pitch = float(np.degrees(np.arctan2(-rmat[1, 2], rmat[1, 1])))
            yaw   = float(np.degrees(np.arctan2(-rmat[2, 0], sy)))
            roll  = 0.0

        return pitch, yaw, roll

    except Exception:
        logger.exception("Error estimating head pose")
        return 0.0, 0.0, 0.0
