import time
import numpy as np
from avp_stream import VisionProStreamer


def safe_first(x):
    """
    把 (1,4,4) 这种数组取成 (4,4)，没有数据时返回 None
    """
    if x is None:
        return None
    arr = np.asarray(x, dtype=np.float32)
    if arr.ndim >= 3 and arr.shape[0] == 1:
        return arr[0]
    return arr


def mat4_pos(T):
    """
    从 4x4 齐次变换矩阵里取 xyz
    """
    if T is None or T.shape != (4, 4):
        return None
    return T[:3, 3]


def main():
    # 改成你在 Vision Pro 里看到的 IP
    avp_ip = "192.168.3.78"

    print(f"Connecting to Vision Pro: {avp_ip}")
    streamer = VisionProStreamer(ip=avp_ip, record=False)

    print("Receiving data... Press Ctrl+C to stop.")
    last_print = time.time()

    while True:
        data = streamer.latest
        if data is None:
            time.sleep(0.01)
            continue

        head = safe_first(data.get("head"))
        left_wrist = safe_first(data.get("left_wrist"))
        right_wrist = safe_first(data.get("right_wrist"))

        left_pinch = data.get("left_pinch_distance", None)
        right_pinch = data.get("right_pinch_distance", None)

        head_xyz = mat4_pos(head)
        left_xyz = mat4_pos(left_wrist)
        right_xyz = mat4_pos(right_wrist)

        now = time.time()
        if now - last_print > 0.5:
            print("----- frame -----")
            print("head xyz       :", None if head_xyz is None else np.round(head_xyz, 4))
            print("left wrist xyz :", None if left_xyz is None else np.round(left_xyz, 4))
            print("right wrist xyz:", None if right_xyz is None else np.round(right_xyz, 4))
            print("left pinch     :", left_pinch)
            print("right pinch    :", right_pinch)

            # 看看还返回了哪些字段
            print("keys:", list(data.keys()))
            last_print = now

        time.sleep(0.005)


if __name__ == "__main__":
    main()
    