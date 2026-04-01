import time
import yaml

from app.avp.streamer import AVPStreamerClient
from app.avp.parser import AVPParser
from app.common.transforms import extract_xyz, format_xyz, fingers_count

from app.common.data_saver import DataSaver


class ReceiverPipeline:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            runtime_cfg = cfg["runtime"]

        self.avp_ip = cfg["avp"]["ip"]
        self.loop_sleep_s = float(runtime_cfg.get("loop_sleep_s", 0.005))
        self.print_interval_s = float(runtime_cfg.get("print_interval_s", 0.5))

        self.streamer = AVPStreamerClient(ip=self.avp_ip, record=False)
        self.parser = AVPParser()

        self.saver = DataSaver()

    def run(self):
        print(f"Connecting to Vision Pro: {self.avp_ip}")
        print("Receiving data... Press Ctrl+C to stop.")

        last_print = time.time()

        try:
            while True:
                raw = self.streamer.get_latest()
                if raw is None:
                    time.sleep(self.loop_sleep_s)
                    continue

                frame = self.parser.parse(raw)

                self.saver.save(frame)

                now = time.time()
                if now - last_print >= self.print_interval_s:
                    head_xyz = extract_xyz(frame.head)
                    left_xyz = extract_xyz(frame.left_wrist)
                    right_xyz = extract_xyz(frame.right_wrist)

                    print("----- frame -----")
                    print(f"timestamp_ns     : {frame.timestamp_ns}")
                    print(f"head xyz         : {format_xyz(head_xyz)}")
                    print(f"left wrist xyz   : {format_xyz(left_xyz)}")
                    print(f"right wrist xyz  : {format_xyz(right_xyz)}")
                    print(f"left pinch       : {frame.left_pinch_distance:.5f}")
                    print(f"right pinch      : {frame.right_pinch_distance:.5f}")
                    print(f"left wrist roll  : {frame.left_wrist_roll:.5f}")
                    print(f"right wrist roll : {frame.right_wrist_roll:.5f}")
                    print(f"left fingers num : {fingers_count(frame.left_fingers)}")
                    print(f"right fingers num: {fingers_count(frame.right_fingers)}")
                    print(f"raw keys         : {list(raw.keys())}")
                    print()

                    last_print = now

                time.sleep(self.loop_sleep_s)

        except KeyboardInterrupt:
            print("\nStopped.")
