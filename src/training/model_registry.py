from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ModelEntry:
    model_id: str
    model_type: str
    version: str = "1.0.0"
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    path: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    status: str = "registered"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ModelRegistry:
    def __init__(self, registry_dir: str = "models"):
        self._registry_dir = registry_dir
        self._entries: Dict[str, ModelEntry] = {}
        os.makedirs(registry_dir, exist_ok=True)
        self._load_registry()

    def register(
        self,
        model_id: str,
        model_type: str,
        version: str = "1.0.0",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ModelEntry:
        now = datetime.now().isoformat()
        entry = ModelEntry(
            model_id=model_id,
            model_type=model_type,
            version=version,
            description=description,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            status="registered",
        )
        self._entries[model_id] = entry
        self._save_registry()
        return entry

    def save_model(
        self,
        model_id: str,
        state: Dict[str, Any],
        path: Optional[str] = None,
    ) -> str:
        if model_id not in self._entries:
            raise KeyError(f"Model '{model_id}' not registered")

        if path is None:
            path = os.path.join(
                self._registry_dir, f"{model_id}.pt"
            )

        self._torch_save(state, path)
        self._entries[model_id].path = path
        self._entries[model_id].updated_at = datetime.now().isoformat()
        self._entries[model_id].status = "saved"
        self._save_registry()
        return path

    def load_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        if model_id not in self._entries:
            return None
        entry = self._entries[model_id]
        if entry.path is None or not os.path.isfile(entry.path):
            return None
        try:
            return self._torch_load(entry.path)
        except Exception:
            return None

    def get(self, model_id: str) -> Optional[ModelEntry]:
        return self._entries.get(model_id)

    def list_models(self, model_type: Optional[str] = None) -> List[ModelEntry]:
        if model_type is None:
            return list(self._entries.values())
        return [
            e for e in self._entries.values()
            if e.model_type == model_type
        ]

    def update_metrics(
        self, model_id: str, metrics: Dict[str, float]
    ) -> None:
        if model_id not in self._entries:
            raise KeyError(f"Model '{model_id}' not registered")
        self._entries[model_id].metrics.update(metrics)
        self._entries[model_id].updated_at = datetime.now().isoformat()
        self._save_registry()

    def register_future(
        self,
        model_type: str,
        description: str = "",
    ) -> ModelEntry:
        model_id = f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return self.register(
            model_id=model_id,
            model_type=model_type,
            version="0.0.0",
            description=description,
            metadata={"future_model": True},
        )

    def _torch_save(self, data: Dict[str, Any], path: str) -> None:
        try:
            import torch
            torch.save(data, path)
        except ImportError:
            import pickle
            with open(path, "wb") as f:
                pickle.dump(data, f)

    def _torch_load(self, path: str) -> Optional[Dict[str, Any]]:
        try:
            import torch
            return torch.load(path, map_location="cpu")
        except ImportError:
            import pickle
            with open(path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None

    def _registry_path(self) -> str:
        return os.path.join(self._registry_dir, "registry.json")

    def _save_registry(self) -> None:
        path = self._registry_path()
        data = {
            mid: entry.to_dict()
            for mid, entry in self._entries.items()
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_registry(self) -> None:
        path = self._registry_path()
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            for mid, entry_data in data.items():
                self._entries[mid] = ModelEntry(**entry_data)
        except Exception:
            pass
