import time
from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock

MAX_KEYS = 10


class KeyNotFoundError(Exception):
    pass


@dataclass
class KVStoreItem:
    value: str
    expires_at: float | None


class KVStore:
    def __init__(self) -> None:
        self._items = OrderedDict()
        self._lock = RLock()

    def put(self, key: str, value: str, ttl_seconds: int) -> None:
        with self._lock:
            expires_at = None

            if ttl_seconds > 0:
                expires_at = time.monotonic() + ttl_seconds

            self._items[key] = KVStoreItem(
                value=value,
                expires_at=expires_at,
            )

            self._items.move_to_end(key)
            if len(self._items) > MAX_KEYS:
                self._del_expired_items()
                self._del_outbounded_items()

    def get(self, key: str) -> str:
        with self._lock:
            item = self._items.get(key)

            if item is None:
                raise KeyNotFoundError
            if self._is_expired(item):
                del self._items[key]
                raise KeyNotFoundError

            self._items.move_to_end(key)
            return item.value

    def delete(self, key: str) -> None:
        with self._lock:
            self._items.pop(key, None)

    def list(self, prefix: str) -> list[tuple[str, str]]:
        with self._lock:
            self._del_expired_items()

            result = []

            for key, item in self._items.items():
                if key.startswith(prefix):
                    result.append((key, item.value))

            return result

    def _is_expired(self, item: KVStoreItem) -> bool:
        return item.expires_at is not None and time.monotonic() >= item.expires_at

    def _del_expired_items(self) -> None:
        expired_keys = [
            key for key, item in self._items.items() if self._is_expired(item)
        ]

        for key in expired_keys:
            del self._items[key]

    def _del_outbounded_items(self) -> None:
        while len(self._items) > MAX_KEYS:
            self._items.popitem(last=False)
