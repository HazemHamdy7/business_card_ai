# Core Public API Report

## Package: `src.core`

Total exports: **54**

### Classes

| Name | Source | Description |
|------|--------|-------------|
| `BusinessCardAIError` | `exceptions.py` | Base exception |
| `CircularDependencyError` | `exceptions.py` | Circular dependency detected |
| `Config` | `config.py` | Singleton configuration |
| `ConfigurationError` | `exceptions.py` | Configuration failure |
| `ConfigurationManager` | `config.py` | Multi-source configuration manager |
| `ConfigurationSource` | `config.py` | Abstract configuration source |
| `ConfigurationValidator` | `config.py` | Configuration validation |
| `DatasetError` | `exceptions.py` | Dataset operation failure |
| `DeviceInfo` | `device.py` | Device information |
| `EnvironmentConfigurationSource` | `config.py` | Environment variable config source |
| `EnvironmentInfo` | `environment.py` | Environment information |
| `EnvironmentLoader` | `config.py` | .env file loader |
| `FileError` | `exceptions.py` | File operation failure |
| `HealthCheckError` | `exceptions.py` | Health check failure |
| `InferenceError` | `exceptions.py` | Inference failure |
| `JsonConfigurationSource` | `config.py` | JSON config source |
| `ModelError` | `exceptions.py` | Model operation failure |
| `Paths` | `paths.py` | Project path resolution |
| `RegistrationError` | `exceptions.py` | Service registration failure |
| `ResourceExhaustedError` | `exceptions.py` | Resource exhaustion |
| `ServiceNotFoundError` | `exceptions.py` | Service not found |
| `Timer` | `timer.py` | Execution timer |
| `ValidationError` | `exceptions.py` | Validation failure |
| `YamlConfigurationSource` | `config.py` | YAML config source |

### Functions

| Name | Source | Signature |
|------|--------|-----------|
| `get_description` | `version.py` | `() -> str` |
| `get_device` | `device.py` | `() -> DeviceInfo` |
| `get_environment_info` | `environment.py` | `() -> dict[str, Any]` |
| `get_full_version` | `version.py` | `() -> str` |
| `get_logger` | `logger.py` | `(name: str | None = None) -> logging.Logger` |
| `get_version` | `version.py` | `() -> str` |
| `setup_logger` | `logger.py` | `(name: str, level: int, log_to_file: bool, log_to_console: bool) -> logging.Logger` |
| `timer_context` | `timer.py` | Context manager |
| `timer_decorator` | `timer.py` | Decorator |

### Constants

| Name | Type | Value |
|------|------|-------|
| `CONFIG_DEVELOPMENT` | `str` | `"development.yaml"` |
| `CONFIG_INFERENCE` | `str` | `"inference.yaml"` |
| `CONFIG_PRODUCTION` | `str` | `"production.yaml"` |
| `CONFIG_TRAINING` | `str` | `"training.yaml"` |
| `DEFAULT_CONFIG_DIR` | `str` | `"config"` |
| `DEFAULT_CONFIG_FILE` | `str` | `"config.yaml"` |
| `DEFAULT_DATASET_DIR` | `str` | `"dataset"` |
| `DEFAULT_DOCS_DIR` | `str` | `"docs"` |
| `DEFAULT_ENCODING` | `str` | `"utf-8"` |
| `DEFAULT_ENV_FILE` | `str` | `".env"` |
| `DEFAULT_LOGS_DIR` | `str` | `"logs"` |
| `DEFAULT_MODELS_DIR` | `str` | `"models"` |
| `LOG_BACKUP_COUNT` | `int` | `5` |
| `LOG_DATE_FORMAT` | `str` | `"%Y-%m-%d %H:%M:%S"` |
| `LOG_FORMAT` | `str` | `"%(asctime)s \| ..."` |
| `LOG_MAX_BYTES` | `int` | `10 * 1024 * 1024` |
| `PROJECT_DESCRIPTION` | `str` | `"Offline AI-powered..."` |
| `PROJECT_NAME` | `str` | `"Business Card AI"` |
| `PROJECT_VERSION` | `str` | `"0.1.0"` |
| `SUCCESS_LEVEL` | `int` | `25` |
| `TIMER_PRECISION` | `int` | `6` |

---

## Package: `src.core.io`

Total exports: **13**

| Name | Source | Description |
|------|--------|-------------|
| `CacheManager` | `cache_manager.py` | Multi-level cache (memory + disk) |
| `CacheEntry` | `cache_manager.py` | Cache entry with TTL |
| `CacheStatistics` | `cache_manager.py` | Cache hit/miss statistics |
| `CachePolicy` | `cache_manager.py` | Cache eviction policy |
| `CacheSerializer` | `cache_manager.py` | Pickle-based serializer |
| `MemoryCache` | `cache_manager.py` | In-memory cache |
| `DiskCache` | `cache_manager.py` | Disk-backed cache |
| `DirectoryManager` | `directory_manager.py` | Directory operations |
| `FileManager` | `file_manager.py` | File operations |
| `ImageIO` | `image_io.py` | Image read/write/convert |
| `JSONIO` | `json_io.py` | JSON serialization |
| `TempManager` | `temp_manager.py` | Temp file/dir management |
| `YAMLIO` | `yaml_io.py` | YAML serialization |

---

## Package: `src.core.runtime`

Total exports: **19**

| Name | Source | Description |
|------|--------|-------------|
| `Counter` | `metrics.py` | Thread-safe counter |
| `DependencyContainer` | `dependency_container.py` | DI container |
| `Gauge` | `metrics.py` | Thread-safe gauge |
| `GPUMonitor` | `gpu_monitor.py` | CUDA GPU monitoring |
| `GPUSnapshot` | `gpu_monitor.py` | GPU state snapshot |
| `HealthCheck` | `health_check.py` | System health checks |
| `HealthCheckResult` | `health_check.py` | Health check result |
| `HealthStatus` | `health_check.py` | Health status enum |
| `Histogram` | `metrics.py` | Value distribution |
| `Lifetime` | `dependency_container.py` | DI lifetime enum |
| `MemoryMonitor` | `memory_monitor.py` | Process memory monitoring |
| `MemorySnapshot` | `memory_monitor.py` | Memory state snapshot |
| `MetricRegistry` | `metrics.py` | Metric registry |
| `PerformanceMonitor` | `performance_monitor.py` | Performance tracking |
| `PerformanceSnapshot` | `performance_monitor.py` | Performance state snapshot |
| `Registration` | `dependency_container.py` | DI registration |
| `RuntimeContext` | `runtime_context.py` | Centralized runtime context |
| `ServiceRegistry` | `service_registry.py` | Name-based service registry |
| `Timer` | `metrics.py` | Duration timer with histogram |

---

## API Stability

**Status: FROZEN**

All public APIs are considered stable and frozen. Future changes require:
- Bug fixes (minor patch)
- Performance improvements (no API change)
- Security fixes (no API change)

Backward compatibility is guaranteed for all public exports in `__init__.py` files.
