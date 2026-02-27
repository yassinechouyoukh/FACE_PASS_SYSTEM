import time
import numpy as np
from ai.types import Track
from ai.tracker.matching import associate

class BoTSORT:
    def __init__(self):
        self.tracks = []
        self.next_id = 0

    def update(self, detections):
        now = time.time()

        if not self.tracks:
            for d in detections:
                self.tracks.append(Track(self.next_id, np.array(d), now))
                self.next_id += 1
            return self.tracks

        row, col = associate(self.tracks, detections)
        updated = []
        used_det = set()

        for r, c in zip(row, col):
            t = self.tracks[r]
            t.bbox = np.array(detections[c])
            t.last_seen = now
            updated.append(t)
            used_det.add(c)

        for i, d in enumerate(detections):
            if i not in used_det:
                updated.append(Track(self.next_id, np.array(d), now))
                self.next_id += 1

        self.tracks = updated
        return self.tracks
