"""
configs/settings.py
-------------------
Centralised configuration for FacePass AiService.
Every value can be overridden by a matching environment variable or
a .env file in the project root (loaded automatically via pydantic-settings).
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = "postgresql://user:pass@localhost:5432/facepass"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # ── Model ───────────────────────────────────────────────────────────────
    model_dir: Path = Path("models")
    model_version: str = "v1"
    model_name: str = "yolo_face.pt"
    arcface_model: str = "buffalo_l"

    # ── Inference ───────────────────────────────────────────────────────────
    device: str = "cuda"                # "cuda" | "cpu"
    detection_conf_threshold: float = 0.5
    detection_input_size: int = 640

    # ── Recognition ─────────────────────────────────────────────────────────
    embed_interval: int = 15            # frames between re-embeddings
    sim_threshold: float = 0.45        # cosine distance threshold

    # ── Behaviour ────────────────────────────────────────────────────────────
    yaw_threshold: float = 20.0        # degrees; beyond = looking away
    pitch_threshold: float = -10.0     # degrees; below = looking down

    # ── Server ──────────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    log_file: str = "logs/facepass.log"

    # ── Scaling ─────────────────────────────────────────────────────────────
    # Set to your Redis URL to enable pub/sub broadcasting of results.
    # Leave empty to use the default in-process WebSocket manager.
    redis_url: str = ""

    # ── Convenience properties ───────────────────────────────────────────────
    @property
    def model_path(self) -> Path:
        """Resolved path to the active YOLO model file."""
        return self.model_dir / self.model_version / self.model_name


# Singleton — import this everywhere
settings = Settings()

# Legacy aliases kept for backwards compatibility with older imports
EMBED_INTERVAL: int = settings.embed_interval
SIM_THRESHOLD: float = settings.sim_threshold
DEVICE: str = settings.device
