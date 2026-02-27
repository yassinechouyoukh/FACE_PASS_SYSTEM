import numpy as np

class KalmanFilter:
    def initiate(self, box):
        mean = np.array(box + box)
        cov = np.eye(8) * 10
        return mean, cov
