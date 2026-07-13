import logging
from pathlib import Path
from typing import Any

from src.core.config import ConfigurationManager
from src.core.device import DeviceInfo, get_device
from src.core.environment import EnvironmentInfo
from src.core.io.cache_manager import CacheManager
from src.core.logger import get_logger, setup_logger
from src.core.paths import Paths
from src.core.version import get_full_version, get_version


class RuntimeContext:
    def __init__(
        self,
        config_manager: ConfigurationManager | None = None,
        logger_name: str = "business_card_ai",
        cache_dir: str | None = None,
    ) -> None:
        self._config_manager = config_manager or ConfigurationManager()
        self._config_manager.load()
        self._logger = setup_logger(logger_name)
        self._device_info = None
        self._environment_info = None
        self._cache_manager: CacheManager | None = None
        self._cache_dir = cache_dir
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        Paths.ensure_dirs()
        self._config_manager.load()
        self._device_info = get_device()
        self._environment_info = EnvironmentInfo()
        cache_path = Paths.root() / "cache" if not self._cache_dir else Path(self._cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        self._cache_manager = CacheManager(cache_dir=cache_path)
        self._initialized = True

    @property
    def config(self) -> ConfigurationManager:
        return self._config_manager

    @property
    def logger(self) -> logging.Logger:
        return get_logger()

    @property
    def device(self) -> DeviceInfo:
        if self._device_info is None:
            self._device_info = get_device()
        return self._device_info

    @property
    def environment(self) -> EnvironmentInfo:
        if self._environment_info is None:
            self._environment_info = EnvironmentInfo()
        return self._environment_info

    @property
    def cache(self) -> CacheManager:
        if self._cache_manager is None:
            cache_path = Paths.root() / "cache"
            cache_path.mkdir(parents=True, exist_ok=True)
            self._cache_manager = CacheManager(cache_dir=cache_path)
        return self._cache_manager

    @property
    def paths(self) -> type:
        return Paths

    @property
    def version(self) -> str:
        return get_version()

    @property
    def full_version(self) -> str:
        return get_full_version()

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "full_version": self.full_version,
            "device": self.device.to_dict(),
            "environment": self.environment.to_dict(),
            "initialized": self._initialized,
        }
