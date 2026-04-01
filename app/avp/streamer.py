from avp_stream import VisionProStreamer


class AVPStreamerClient:
    def __init__(self, ip: str, record: bool = False):
        self.ip = ip
        self.record = record
        self._streamer = VisionProStreamer(ip=ip, record=record)

    def get_latest(self):
        return self._streamer.latest
    