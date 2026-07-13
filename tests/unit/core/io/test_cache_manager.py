import time
from pathlib import Path

import pytest

from src.core.io.cache_manager import (
    CacheEntry,
    CacheManager,
    CachePolicy,
    CacheSerializer,
    CacheStatistics,
    DiskCache,
    MemoryCache,
)


class TestCacheEntry:
    def test_creation(self) -> None:
        entry = CacheEntry("k", "v")
        assert entry.key == "k"
        assert entry.value == "v"
        assert entry.expires_at is None
        assert entry.created_at > 0
        assert not entry.is_expired

    def test_expiry(self) -> None:
        entry = CacheEntry("k", "v", expires_at=time.time() - 1)
        assert entry.is_expired

    def test_not_expired(self) -> None:
        entry = CacheEntry("k", "v", expires_at=time.time() + 100)
        assert not entry.is_expired

    def test_size(self) -> None:
        entry = CacheEntry("k", "hello")
        assert entry.size > 0

    def test_touch(self) -> None:
        entry = CacheEntry("k", "v")
        old = entry.last_access
        time.sleep(0.001)
        entry.touch()
        assert entry.last_access > old


class TestCacheStatistics:
    def test_hit_ratio_zero(self) -> None:
        stats = CacheStatistics()
        assert stats.hit_ratio == 0.0

    def test_hit_ratio_perfect(self) -> None:
        stats = CacheStatistics(hits=10, misses=0)
        assert stats.hit_ratio == 1.0

    def test_hit_ratio_half(self) -> None:
        stats = CacheStatistics(hits=5, misses=5)
        assert stats.hit_ratio == 0.5

    def test_to_dict(self) -> None:
        stats = CacheStatistics(hits=3, misses=1, memory_entries=5, disk_entries=2)
        d = stats.to_dict()
        assert d["hits"] == 3
        assert d["misses"] == 1
        assert d["hit_ratio"] == 0.75
        assert d["memory_entries"] == 5
        assert d["disk_entries"] == 2


class TestCachePolicy:
    def test_default_creation(self) -> None:
        policy = CachePolicy()
        assert policy.default_ttl is None
        assert policy.max_memory_entries is None
        assert policy.max_disk_size is None

    def test_custom_values(self) -> None:
        policy = CachePolicy(default_ttl=60.0, max_memory_entries=100, max_disk_size=1000000)
        assert policy.default_ttl == 60.0
        assert policy.max_memory_entries == 100
        assert policy.max_disk_size == 1000000


class TestCacheSerializer:
    def test_roundtrip(self) -> None:
        data = {"key": "value", "num": 42}
        serialized = CacheSerializer.serialize(data)
        deserialized = CacheSerializer.deserialize(serialized)
        assert deserialized == data

    def test_string(self) -> None:
        serialized = CacheSerializer.serialize("hello")
        assert CacheSerializer.deserialize(serialized) == "hello"

    def test_none(self) -> None:
        serialized = CacheSerializer.serialize(None)
        assert CacheSerializer.deserialize(serialized) is None


class TestMemoryCache:
    def test_put_and_get(self) -> None:
        cache = MemoryCache[str]()
        cache.put("k", "v")
        assert cache.get("k") == "v"

    def test_get_missing(self) -> None:
        cache = MemoryCache[str]()
        assert cache.get("missing") is None

    def test_remove(self) -> None:
        cache = MemoryCache[str]()
        cache.put("k", "v")
        cache.remove("k")
        assert cache.get("k") is None

    def test_contains(self) -> None:
        cache = MemoryCache[str]()
        cache.put("k", "v")
        assert cache.contains("k")
        assert not cache.contains("missing")

    def test_clear(self) -> None:
        cache = MemoryCache[str]()
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        cache.clear()
        assert cache.size() == 0

    def test_size(self) -> None:
        cache = MemoryCache[str]()
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        assert cache.size() == 2

    def test_ttl_expiry(self) -> None:
        cache = MemoryCache[str]()
        cache.put("k", "v", ttl=0.01)
        time.sleep(0.02)
        assert cache.get("k") is None

    def test_cleanup(self) -> None:
        cache = MemoryCache[str]()
        cache.put("k1", "v1", ttl=0.01)
        cache.put("k2", "v2")
        time.sleep(0.02)
        removed = cache.cleanup()
        assert removed == 1
        assert cache.size() == 1

    def test_eviction(self) -> None:
        policy = CachePolicy(max_memory_entries=2)
        cache = MemoryCache[str](policy)
        cache.put("k1", "v1")
        cache.put("k2", "v2")
        cache.put("k3", "v3")
        assert cache.size() == 2


class TestDiskCache:
    def test_save_and_load(self, tmp_path: Path) -> None:
        cache = DiskCache(tmp_path / "cache")
        cache.save("k", {"nested": "value"})
        assert cache.load("k") == {"nested": "value"}

    def test_load_missing(self, tmp_path: Path) -> None:
        cache = DiskCache(tmp_path / "cache")
        assert cache.load("missing") is None

    def test_exists(self, tmp_path: Path) -> None:
        cache = DiskCache(tmp_path / "cache")
        cache.save("k", "v")
        assert cache.exists("k")
        assert not cache.exists("missing")

    def test_delete(self, tmp_path: Path) -> None:
        cache = DiskCache(tmp_path / "cache")
        cache.save("k", "v")
        cache.delete("k")
        assert not cache.exists("k")

    def test_clear(self, tmp_path: Path) -> None:
        cache = DiskCache(tmp_path / "cache")
        cache.save("k1", "v1")
        cache.save("k2", "v2")
        cache.clear()
        assert cache.entry_count() == 0

    def test_entry_count(self, tmp_path: Path) -> None:
        cache = DiskCache(tmp_path / "cache")
        assert cache.entry_count() == 0
        cache.save("k1", "v1")
        assert cache.entry_count() == 1

    def test_size_bytes(self, tmp_path: Path) -> None:
        cache = DiskCache(tmp_path / "cache")
        cache.save("k", "v")
        assert cache.size_bytes() > 0

    def test_ttl_expiry(self, tmp_path: Path) -> None:
        cache = DiskCache(tmp_path / "cache")
        cache.save("k", "v", ttl=0.01)
        time.sleep(0.02)
        assert cache.load("k") is None


class TestCacheManager:
    def test_memory_only(self) -> None:
        cm = CacheManager[str]()
        cm.put("k", "v")
        assert cm.get("k") == "v"
        assert cm.contains("k")

    def test_with_disk(self, tmp_path: Path) -> None:
        cm = CacheManager[str](cache_dir=tmp_path / "cm")
        cm.put("k", "v")
        assert cm.get("k") == "v"

    def test_remove(self) -> None:
        cm = CacheManager[str]()
        cm.put("k", "v")
        cm.remove("k")
        assert not cm.contains("k")

    def test_clear(self) -> None:
        cm = CacheManager[str]()
        cm.put("k1", "v1")
        cm.put("k2", "v2")
        cm.clear()
        assert cm.size() == 0

    def test_miss(self) -> None:
        cm = CacheManager[str]()
        assert cm.get("missing") is None
        assert cm.stats.misses == 1

    def test_stats(self) -> None:
        cm = CacheManager[str]()
        cm.get("miss1")
        cm.get("miss2")
        cm.put("hit", "v")
        cm.get("hit")
        stats = cm.stats
        assert stats.hits == 1
        assert stats.misses >= 2
        assert stats.hit_ratio > 0

    def test_cleanup(self) -> None:
        cm = CacheManager[str]()
        cm.put("k", "v", ttl=0.01)
        time.sleep(0.02)
        removed = cm.cleanup()
        assert removed >= 1

    def test_ttl(self) -> None:
        cm = CacheManager[str]()
        cm.put("k", "v", ttl=0.01)
        time.sleep(0.02)
        assert cm.get("k") is None
