import time
import numpy as np
import signal
import sys
from avp_stream import VisionProStreamer


def safe_first(x):
    """把 (1,4,4) 这种数组取成 (4,4)，没有数据时返回 None"""
    if x is None:
        return None
    arr = np.asarray(x, dtype=np.float32)
    if arr.ndim >= 3 and arr.shape[0] == 1:
        return arr[0]
    return arr


def mat4_pos(T):
    """从 4x4 齐次变换矩阵里取 xyz"""
    if T is None or T.shape != (4, 4):
        return None
    return T[:3, 3]


class VisionProClient:
    def __init__(self, ip):
        self.ip = ip
        self.streamer = None
        self.running = True
        self.last_print = time.time()

        # 注册信号处理，确保 Ctrl+C 能清理资源
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("\n收到中断信号，正在清理资源...")
        self.running = False

    def _cleanup(self):
        """确保资源被释放"""
        if self.streamer is not None:
            try:
                # 尝试关闭连接（如果 avp_stream 支持）
                if hasattr(self.streamer, 'close'):
                    self.streamer.close()
                if hasattr(self.streamer, 'stop'):
                    self.streamer.stop()
                # 强制删除引用
                del self.streamer
            except Exception as e:
                print(f"清理时出错: {e}")
            finally:
                self.streamer = None
                print("资源已清理")

    def _connect(self):
        """建立连接，带重试机制"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"尝试连接 {self.ip} (第 {attempt + 1} 次)...")
                # 如果之前有连接，先清理
                self._cleanup()
                # 等待端口释放（关键！）
                time.sleep(0.5)

                self.streamer = VisionProStreamer(ip=self.ip, record=False)
                # 验证连接是否成功
                time.sleep(0.1)
                test_data = self.streamer.latest
                if test_data is not None:
                    print("连接成功！")
                    return True
                else:
                    print("连接无数据，重试...")

            except Exception as e:
                print(f"连接失败: {e}")
                time.sleep(1)

        return False

    def run(self):
        """主循环"""
        if not self._connect():
            print("无法建立连接，退出")
            return

        print("接收数据中... 按 Ctrl+C 停止")

        try:
            while self.running:
                try:
                    data = self.streamer.latest
                    if data is None:
                        time.sleep(0.01)
                        continue

                    # 解析数据
                    head = safe_first(data.get("head"))
                    left_wrist = safe_first(data.get("left_wrist"))
                    right_wrist = safe_first(data.get("right_wrist"))
                    left_pinch = data.get("left_pinch_distance")
                    right_pinch = data.get("right_pinch_distance")

                    head_xyz = mat4_pos(head)
                    left_xyz = mat4_pos(left_wrist)
                    right_xyz = mat4_pos(right_wrist)

                    # 打印信息
                    now = time.time()
                    if now - self.last_print > 0.5:
                        print("----- frame -----")
                        print("head xyz       :", None if head_xyz is None else np.round(head_xyz, 4))
                        print("left wrist xyz :", None if left_xyz is None else np.round(left_xyz, 4))
                        print("right wrist xyz:", None if right_xyz is None else np.round(right_xyz, 4))
                        print("left pinch     :", left_pinch)
                        print("right pinch    :", right_pinch)
                        print("keys:", list(data.keys()))
                        self.last_print = now

                    time.sleep(0.005)

                except Exception as e:
                    print(f"数据读取错误: {e}")
                    # 尝试重新连接
                    if not self._connect():
                        break

        finally:
            self._cleanup()


def main():
    avp_ip = "192.168.3.78"
    client = VisionProClient(avp_ip)
    client.run()


if __name__ == "__main__":
    main()