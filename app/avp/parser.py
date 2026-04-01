import time
import numpy as np

from app.common.types import AVPFrame
from app.common.transforms import safe_array, safe_first_matrix


class AVPParser:
    def parse(self, raw: dict) -> AVPFrame:
        if raw is None:
            raise ValueError("raw data is None")

        head = safe_first_matrix(raw.get("head"))
        left_wrist = safe_first_matrix(raw.get("left_wrist"))
        right_wrist = safe_first_matrix(raw.get("right_wrist"))

        left_fingers = safe_array(raw.get("left_fingers"))
        right_fingers = safe_array(raw.get("right_fingers"))

        return AVPFrame(
            timestamp_ns=time.time_ns(),
            head=head,
            left_wrist=left_wrist,
            right_wrist=right_wrist,
            left_fingers=left_fingers,
            right_fingers=right_fingers,
            left_pinch_distance=float(raw.get("left_pinch_distance", 0.0)),
            right_pinch_distance=float(raw.get("right_pinch_distance", 0.0)),
            left_wrist_roll=float(raw.get("left_wrist_roll", 0.0)),
            right_wrist_roll=float(raw.get("right_wrist_roll", 0.0)),
        )
