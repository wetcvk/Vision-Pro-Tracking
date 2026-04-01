import json
import os
import time
from datetime import datetime

import numpy as np


class DataSaver:
    def __init__(self, filename=None):  # 改为 None，避免默认参数求值陷阱
        # 实例化时生成文件名格式为 tracking_MMDDHHMMSS.jsonl 的记录文件
        if filename is None:
            filename = f"tracking_{datetime.now().strftime('%m%d%H%M%S')}.jsonl"

        # 路径处理
        current_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(current_dir)
        data_dir = os.path.join(app_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        self.save_path = os.path.join(data_dir, filename)
        self.f = open(self.save_path, "a", encoding="utf-8")
        self.frame_id = 0

    def _to_list(self, arr):
        if arr is None:
            return None
        if isinstance(arr, np.ndarray):
            return arr.tolist()
        return arr

    def save(self, frame):
        self.frame_id += 1

        record = {
            "frame_id": self.frame_id,
            "timestamp_ns": frame.timestamp_ns,
            "head": self._to_list(frame.head),
            "left_wrist": self._to_list(frame.left_wrist),
            "right_wrist": self._to_list(frame.right_wrist),
            "left_fingers": self._to_list(frame.left_fingers),
            "right_fingers": self._to_list(frame.right_fingers),
            "left_pinch_distance": frame.left_pinch_distance,
            "right_pinch_distance": frame.right_pinch_distance,
            "left_wrist_roll": frame.left_wrist_roll,
            "right_wrist_roll": frame.right_wrist_roll,
        }

        self.f.write(json.dumps(record) + "\n")
        self.f.flush()

    def close(self):
        """安全关闭文件"""
        if hasattr(self, 'f') and self.f and not self.f.closed:
            self.f.close()

    def __del__(self):
        """析构时兜底关闭"""
        self.close()

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False