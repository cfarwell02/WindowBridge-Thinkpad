import queue
import threading

import av


class VideoFeed:
    def __init__(self, address):
        self.address = address
        self.frames = queue.Queue(maxsize=1)
        self.messages = queue.SimpleQueue()
        self.stopping = threading.Event()
        self.thread = threading.Thread(
            target=self._receive,
            daemon=True,
        )

    def start(self):
        self.thread.start()

    def stop(self):
        self.stopping.set()
        self.thread.join(timeout=0.2)

    def _receive(self):
        try:
            with av.open(
                self.address,
                format="h264",
                timeout=(15.0, 15.0),
            ) as container:
                for frame in container.decode(video=0):
                    if self.stopping.is_set():
                        break

                    try:
                        self.frames.put_nowait(frame)
                    except queue.Full:
                        pass

        except Exception as error:
            if not self.stopping.is_set():
                self.messages.put(f"Video error: {error}")
        finally:
            self.messages.put("Video feed stopped.")
