import pytest

from src.training.seed_manager import SeedManager


class TestSeedManager:
    def test_seed_all(self):
        sm = SeedManager(seed=42, deterministic=False)
        result = sm.seed_all()
        assert result == 42

    def test_custom_seed(self):
        sm = SeedManager(seed=42)
        result = sm.seed_all(seed=99)
        assert result == 99

    def test_properties(self):
        sm = SeedManager(seed=42, deterministic=True)
        assert sm.seed == 42
        assert sm.deterministic is True

    def test_set_deterministic(self):
        sm = SeedManager(seed=42, deterministic=False)
        sm.set_deterministic(True)
        assert sm.deterministic is True

    def test_seed_reproducibility(self):
        sm = SeedManager(seed=42)
        sm.seed_all()
        import random
        r1 = random.random()

        sm2 = SeedManager(seed=42)
        sm2.seed_all()
        random.seed(42)
        r2 = random.random()

        assert r1 == r2
