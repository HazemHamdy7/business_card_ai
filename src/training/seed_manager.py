from __future__ import annotations

import os
import random
from typing import Optional

import numpy as np


class SeedManager:
    def __init__(self, seed: int = 42, deterministic: bool = True):
        self._seed = seed
        self._deterministic = deterministic

    def seed_all(self, seed: Optional[int] = None) -> int:
        actual_seed = seed if seed is not None else self._seed
        random.seed(actual_seed)
        np.random.seed(actual_seed)
        self._seed_torch(actual_seed)
        self._seed_cuda(actual_seed)
        return actual_seed

    def _seed_torch(self, seed: int) -> None:
        try:
            import torch
            torch.manual_seed(seed)
        except ImportError:
            pass

    def _seed_cuda(self, seed: int) -> None:
        if not self._deterministic:
            return
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
                if self._deterministic:
                    torch.backends.cudnn.deterministic = True
                    torch.backends.cudnn.benchmark = False
        except ImportError:
            pass

    def set_deterministic(self, enabled: bool) -> None:
        self._deterministic = enabled
        if enabled:
            os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
            try:
                import torch
                torch.use_deterministic_algorithms(True)
            except ImportError:
                pass

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def deterministic(self) -> bool:
        return self._deterministic
