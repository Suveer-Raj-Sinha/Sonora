import time
from typing import Any

class TTLCache:
    def __init__(self, ttl: int = 900):
        self.ttl = ttl
        self.data: dict[str, tuple[float, Any]] = {}

    def get(self, key: str):
        item = self.data.get(key)
        if not item:
            return None
        expires, value = item
        if expires < time.time():
            self.data.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any):
        self.data[key] = (time.time() + self.ttl, value)

    def clear(self):
        self.data.clear()
