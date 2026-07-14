from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Checkpoint:
    path: str
    epoch: int
    score: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_best: bool = False
    is_last: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CheckpointManager:
    def __init__(
        self,
        save_dir: str = "checkpoints",
        max_checkpoints: int = 5,
        keep_last: bool = True,
        save_best_only: bool = False,
    ):
        self._save_dir = save_dir
        self._max_checkpoints = max_checkpoints
        self._keep_last = keep_last
        self._save_best_only = save_best_only
        self._checkpoints: List[Checkpoint] = []
        self._best_score: float = float("-inf")
        self._best_path: Optional[str] = None
        self._last_path: Optional[str] = None
        os.makedirs(save_dir, exist_ok=True)

    def save(
        self,
        state: Dict[str, Any],
        epoch: int,
        score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Checkpoint:
        timestamp = datetime.now().isoformat()
        is_best = score > self._best_score
        if is_best:
            self._best_score = score

        filename = f"epoch_{epoch:04d}_score_{score:.4f}.pt"
        path = os.path.join(self._save_dir, filename)

        checkpoint_data = {
            "epoch": epoch,
            "score": score,
            "timestamp": timestamp,
            "is_best": is_best,
            "state_dict": state,
            "metadata": metadata or {},
        }
        torch_save(checkpoint_data, path)

        cp = Checkpoint(
            path=path,
            epoch=epoch,
            score=score,
            timestamp=timestamp,
            metadata=metadata or {},
            is_best=is_best,
            is_last=True,
        )

        if self._last_path and self._keep_last:
            last_checkpoint = self._find_checkpoint(self._last_path)
            if last_checkpoint:
                last_checkpoint.is_last = False

        self._last_path = path
        self._checkpoints.append(cp)

        if is_best:
            best_path = os.path.join(self._save_dir, "best.pt")
            shutil.copy2(path, best_path)
            self._best_path = best_path

        if self._save_best_only and not is_best:
            os.remove(path)
            self._checkpoints.remove(cp)
            return Checkpoint(
                path="",
                epoch=epoch,
                score=score,
                timestamp=timestamp,
                metadata=metadata or {},
                is_best=False,
                is_last=False,
            )

        self._cleanup()

        return cp

    def load(
        self,
        path: str,
    ) -> Optional[Dict[str, Any]]:
        if not os.path.isfile(path):
            return None
        try:
            return torch_load(path)
        except Exception:
            return None

    def load_best(self) -> Optional[Dict[str, Any]]:
        best_path = os.path.join(self._save_dir, "best.pt")
        return self.load(best_path)

    def load_last(self) -> Optional[Dict[str, Any]]:
        if self._last_path and os.path.isfile(self._last_path):
            return self.load(self._last_path)
        checkpoints = self.list_checkpoints()
        if checkpoints:
            return self.load(checkpoints[-1].path)
        return None

    def list_checkpoints(self) -> List[Checkpoint]:
        checkpoints = []
        if not os.path.isdir(self._save_dir):
            return checkpoints
        for fname in sorted(os.listdir(self._save_dir)):
            if fname.endswith(".pt"):
                path = os.path.join(self._save_dir, fname)
                try:
                    data = torch_load(path)
                    cp = Checkpoint(
                        path=path,
                        epoch=data.get("epoch", 0),
                        score=data.get("score", 0.0),
                        timestamp=data.get("timestamp", ""),
                        metadata=data.get("metadata", {}),
                        is_best=data.get("is_best", False),
                        is_last=(fname == "last.pt"),
                    )
                    checkpoints.append(cp)
                except Exception:
                    continue
        return sorted(checkpoints, key=lambda c: c.epoch)

    def _find_checkpoint(self, path: str) -> Optional[Checkpoint]:
        for cp in self._checkpoints:
            if cp.path == path:
                return cp
        return None

    def _cleanup(self) -> None:
        if self._max_checkpoints <= 0:
            return
        all_cps = self.list_checkpoints()
        keep = set()
        if all_cps:
            if self._keep_last:
                keep.add(all_cps[-1].path)
            best_path = os.path.join(self._save_dir, "best.pt")
            if os.path.isfile(best_path):
                keep.add(best_path)

            sorted_cps = sorted(all_cps, key=lambda c: c.score, reverse=True)
            for cp in sorted_cps[:self._max_checkpoints]:
                keep.add(cp.path)

            for cp in all_cps:
                if cp.path not in keep and os.path.isfile(cp.path):
                    try:
                        os.remove(cp.path)
                    except Exception:
                        pass

    def get_best_score(self) -> float:
        return self._best_score

    def get_best_path(self) -> Optional[str]:
        return self._best_path

    def summary(self) -> Dict[str, Any]:
        return {
            "save_dir": self._save_dir,
            "max_checkpoints": self._max_checkpoints,
            "best_score": self._best_score,
            "best_path": self._best_path,
            "last_path": self._last_path,
            "total_checkpoints": len(self._checkpoints),
        }


def torch_save(data: Dict[str, Any], path: str) -> None:
    try:
        import torch
        torch.save(data, path)
    except ImportError:
        import pickle
        with open(path, "wb") as f:
            pickle.dump(data, f)


def torch_load(path: str) -> Optional[Dict[str, Any]]:
    try:
        import torch
        return torch.load(path, map_location="cpu")
    except ImportError:
        import pickle
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None
