import json
import socket


class InputSender:
    def __init__(self):
        self.connection = socket.create_connection(
            ("127.0.0.1", 5001),
            timeout=2.0,
        )
        self.connection.setsockopt(
            socket.IPPROTO_TCP,
            socket.TCP_NODELAY,
            1,
        )

    def _send(self, event_type, x, y):
        message = {
            "type": event_type,
            "x": x,
            "y": y,
        }
        data = (
            json.dumps(message, allow_nan=False) + "\n"
        ).encode("utf-8")
        self.connection.sendall(data)

    def move_mouse(self, x, y):
        self._send("mouseMove", x, y)

    def set_left_button(self, pressed, x, y):
        event_type = "leftMouseDown" if pressed else "leftMouseUp"
        self._send(event_type, x, y)

    def close(self):
        self.connection.close()
