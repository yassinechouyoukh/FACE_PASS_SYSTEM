from dataclasses import dataclass
import numpy as np
import time

@dataclass
class Track:
    track_id: int
    bbox: np.ndarray
    last_seen: float
    embedding: np.ndarray | None = None
    last_embed_frame: int = 0
