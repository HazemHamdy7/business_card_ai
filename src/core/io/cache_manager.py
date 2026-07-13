import json
import pickle
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generic, TypeVar

from src.core.exceptions import FileError

T = TypeVar("T")

@dataclass
class CacheEntry(Generic[T]):
    key: str
    value: T
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    last_access: float = field(default_factory=time.time)

    @property
    def size(self) -> int:
        return len(pickle.dumps(self.value, protocol=pickle.HIGHEST_PROTOCOL))

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def touch(self) -> None:
        self.last_access = time.time()


@dataclass
class CacheStatistics:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired_entries: int = 0
    memory_entries: int = 0
    disk_entries: int = 0
    memory_usage: int = 0
    disk_usage: int = 0

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 4) if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.hit_ratio,
            "evictions": self.evictions,
            "expired_entries": self.expired_entries,
            "memory_entries": self.memory_entries,
            "disk_entries": self.disk_entries,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
        }


@dataclass
class CachePolicy:
    default_ttl: float | None = None
    max_memory_entries: int | None = None
    max_disk_size: int | None = None


class CacheSerializer:
    @staticmethod
    def serialize(value: Any) -> bytes:
        return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def deserialize(data: bytes) -> Any:
        return pickle.loads(data)


class MemoryCache(Generic[T]):
    def __init__(self, policy: CachePolicy | None = None) -> None:
        self._store: dict[str, CacheEntry[T]] = {}
        self._lock = threading.Lock()
        self._policy = policy or CachePolicy()

    def get(self, key: str) -> T | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.is_expired:
                del self._store[key]
                return None
            entry.touch()
            return entry.value

    def put(self, key: str, value: T, ttl: float | None = None) -> None:
        expires_at: float | None = None
        if ttl is not None:
            expires_at = time.time() + ttl
        elif self._policy.default_ttl is not None:
            expires_at = time.time() + self._policy.default_ttl
        entry = CacheEntry(key=key, value=value, expires_at=expires_at)

        with self._lock:
            if self._policy.max_memory_entries and len(self._store) >= self._policy.max_memory_entries:
                self._evict_one()
            self._store[key] = entry

    def remove(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def contains(self, key: str) -> bool:
        return self.get(key) is not None

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._store)

    def cleanup(self) -> int:
        removed = 0
        with self._lock:
            expired_keys = [k for k, v in self._store.items() if v.is_expired]
            for k in expired_keys:
                del self._store[k]
                removed += 1
        return removed

    def _evict_one(self) -> None:
        if not self._store:
            return
        oldest = min(self._store.keys(), key=lambda k: self._store[k].last_access)
        del self._store[oldest]


class DiskCache:
    def __init__(self, cache_dir: Path, policy: CachePolicy | None = None) -> None:
        self._cache_dir = cache_dir
        self._policy = policy or CachePolicy()
        self._lock = threading.Lock()
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, value: Any, ttl: float | None = None) -> None:
        expires_at: float | None = None
        if ttl is not None:
            expires_at = time.time() + ttl
        elif self._policy.default_ttl is not None:
            expires_at = time.time() + self._policy.default_ttl
        data = {"value": value, "expires_at": expires_at, "created_at": time.time()}
        path = self._key_path(key)
        with self._lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(CacheSerializer.serialize(data))

    def load(self, key: str) -> Any | None:
        path = self._key_path(key)
        if not path.exists():
            return None
        try:
            data = CacheSerializer.deserialize(path.read_bytes())
            expires_at = data.get("expires_at")
            if expires_at is not None and time.time() > expires_at:
                path.unlink(missing_ok=True)
                return None
            return data["value"]
        except Exception:
            return None

    def delete(self, key: str) -> None:
        path = self._key_path(key)
        with self._lock:
            path.unlink(missing_ok=True)

    def exists(self, key: str) -> bool:
        return self._key_path(key).exists()

    def clear(self) -> None:
        with self._lock:
            if self._cache_dir.exists():
                import shutil
                shutil.rmtree(str(self._cache_dir))
                self._cache_dir.mkdir(parents=True, exist_ok=True)

    def cleanup(self) -> int:
        removed = 0
        with self._lock:
            for path in list(self._cache_dir.glob("*")):
                if not path.is_file():
                    continue
                try:
                    data = CacheSerializer.deserialize(path.read_bytes())
                    expires_at = data.get("expires_at")
                    if expires_at is not None and time.time() > expires_at:
                        path.unlink()
                        removed += 1
                except Exception:
                    continue
        return removed

    def entry_count(self) -> int:
        if not self._cache_dir.exists():
            return 0
        return len(list(self._cache_dir.iterdir()))

    def size_bytes(self) -> int:
        if not self._cache_dir.exists():
            return 0
        total = 0
        for path in self._cache_dir.rglob("*"):
            if path.is_file():
                total += path.stat().st_size
        return total

    def _key_path(self, key: str) -> Path:
        import hashlib
        hashed = hashlib.sha256(key.encode()).hexdigest()
        return self._cache_dir / f"{hashed}.cache"


class CacheManager(Generic[T]):
    def __init__(self, cache_dir: Path | None = None, policy: CachePolicy | None = None):
        self._policy = policy or CachePolicy()
        self._memory = MemoryCache[T](self._policy)
        self._disk = DiskCache(cache_dir, self._policy) if cache_dir else None
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> T | None:
        value = self._memory.get(key)
        if value is not None:
            self._hits += 1
            return value
        if self._disk is not None:
            value = self._disk.load(key)
            if value is not None:
                self._memory.put(key, value)
                self._hits += 1
                return value
        self._misses += 1
        return None

    def put(self, key: str, value: T, ttl: float | None = None) -> None:
        self._memory.put(key, value, ttl)
        if self._disk is not None:
            self._disk.save(key, value, ttl)

    def remove(self, key: str) -> None:
        self._memory.remove(key)
        if self._disk is not None:
            self._disk.delete(key)

    def contains(self, key: str) -> bool:
        if self._memory.contains(key):
            return True
        if self._disk is not None and self._disk.exists(key):
            return True
        return False

    def clear(self) -> None:
        self._memory.clear()
        if self._disk is not None:
            self._disk.clear()
        self._hits = 0
        self._misses = 0

    def size(self) -> int:
        mem_size = self._memory.size()
        disk_size = self._disk.entry_count() if self._disk else 0
        return mem_size + disk_size

    def cleanup(self) -> int:
        mem_removed = self._memory.cleanup()
        disk_removed = self._disk.cleanup() if self._disk else 0
        return mem_removed + disk_removed

    @property
    def stats(self) -> CacheStatistics:
        hit_count = self._hits
        miss_count = self._misses
        mem_entries = self._memory.size()
        mem_usage = 0
        disk_entries = self._disk.entry_count() if self._disk else 0
        disk_usage = self._disk.size_bytes() if self._disk else 0
        return CacheStatistics(
            hits=hit_count,
            misses=miss_count,
            memory_entries=mem_entries,
            disk_entries=disk_entries,
            memory_usage=mem_usage,
            disk_usage=disk_usage,
        )