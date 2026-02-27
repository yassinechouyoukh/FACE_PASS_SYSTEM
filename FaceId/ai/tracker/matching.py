import numpy as np
from scipy.optimize import linear_sum_assignment

def iou(a, b):
    xA, yA = max(a[0], b[0]), max(a[1], b[1])
    xB, yB = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, xB-xA) * max(0, yB-yA)
    areaA = (a[2]-a[0])*(a[3]-a[1])
    areaB = (b[2]-b[0])*(b[3]-b[1])
    return inter / (areaA+areaB-inter+1e-6)

def associate(tracks, detections):
    cost = np.zeros((len(tracks), len(detections)))
    for i, t in enumerate(tracks):
        for j, d in enumerate(detections):
            cost[i, j] = 1 - iou(t.bbox, d)
    return linear_sum_assignment(cost)
