import numpy as np
from collections import deque

class HybridDetector:
    """
    Detects:
      - Anomaly (fixed): loss > fixed_threshold
      - Spike (adaptive): loss > rolling_mean + z_limit * rolling_std
    Uses a rolling window to estimate mean/std.
    """

    def __init__(self, fixed_threshold: float, window_size: int, z_limit: float, min_warmup: int):
        self.fixed_threshold = fixed_threshold
        self.window_size = window_size
        self.z_limit = z_limit
        self.min_warmup = min_warmup

        self.window = deque(maxlen=window_size)
        self.count = 0

    def update(self, loss: float):
        self.count += 1

        # compute adaptive stats on previous window (before adding this loss)
        if len(self.window) >= 2:
            mean = float(np.mean(self.window))
            std = float(np.std(self.window, ddof=1))
        else:
            mean, std = None, None

        # anomaly (fixed)
        is_anomaly = loss > self.fixed_threshold

        # spike (adaptive)
        is_spike = False
        if self.count > self.min_warmup and mean is not None and std is not None:
            threshold = mean + self.z_limit * (std if std > 1e-12 else 0.0)
            is_spike = loss > threshold
        else:
            threshold = None

        # push current loss to window
        self.window.append(loss)

        return {
            "is_anomaly": is_anomaly,
            "is_spike": is_spike,
            "rolling_mean": mean,
            "rolling_std": std,
            "adaptive_threshold": threshold
        }
