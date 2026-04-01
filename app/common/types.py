from dataclasses import dataclass
import numpy as np


@dataclass
class AVPFrame:
    timestamp_ns: int
    head: np.ndarray | None
    left_wrist: np.ndarray | None
    right_wrist: np.ndarray | None
    left_fingers: np.ndarray | None
    right_fingers: np.ndarray | None
    left_pinch_distance: float
    right_pinch_distance: float
    left_wrist_roll: float
    right_wrist_roll: float
