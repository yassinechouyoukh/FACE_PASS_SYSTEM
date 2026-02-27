"""
behavior/engagement.py
-----------------------
Compute an engagement level from head pose angles.

Engagement is defined as the degree to which a student is oriented
toward the camera (proxy for paying attention).

Levels:
  - ``"high"``   — face roughly centred, within normal thresholds
  - ``"medium"`` — slight deviation; partially distracted
  - ``"low"``    — large deviation; likely not attending
"""

from __future__ import annotations

from configs.settings import settings

# Engagement thresholds (degrees)
_YAW_HIGH:   float = settings.yaw_threshold          # e.g. 20°
_YAW_MEDIUM: float = settings.yaw_threshold * 1.5    # e.g. 30°
_PITCH_HIGH:  float = settings.pitch_threshold        # e.g. -10°
_PITCH_MEDIUM: float = settings.pitch_threshold * 1.5  # e.g. -15°


def compute_engagement(pitch: float, yaw: float) -> str:
    """Classify engagement level from head pose angles.

    Args:
        pitch: Head pitch in degrees (negative = looking down).
        yaw:   Head yaw in degrees (positive = looking right).

    Returns:
        One of ``"high"``, ``"medium"``, or ``"low"``.
    """
    if abs(yaw) > _YAW_MEDIUM or pitch < _PITCH_MEDIUM:
        return "low"
    if abs(yaw) > _YAW_HIGH or pitch < _PITCH_HIGH:
        return "medium"
    return "high"


# Backwards-compatible alias used by older code
def engagement(pitch: float, yaw: float) -> str:
    """Alias for :func:`compute_engagement` (backwards compatibility)."""
    return compute_engagement(pitch, yaw)
