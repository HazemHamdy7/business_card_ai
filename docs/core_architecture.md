# Core Architecture Report

## Architecture Overview

The Business Card AI Core Infrastructure follows Clean Architecture principles with strict layer separation.

### Layer Hierarchy

```
┌─────────────────────────────────────┐
│           Runtime Layer              │
│  DI, Monitoring, Metrics, Health     │
├─────────────────────────────────────┤
│            I/O Layer                 │
│  Cache, File, Image, Serialization   │
├─────────────────────────────────────┤
│         Core Abstractions            │
│  Config, Paths, Device, Exceptions   │
└─────────────────────────────────────┘
```

**Dependency Rule:** Dependencies point inward. No layer depends on an outer layer.

---

## Module Architecture

### 1. Core Abstractions (`src/core/`)

| Module | Responsibility | Key Classes |
|--------|---------------|-------------|
| `config.py` | Configuration loading, validation, management | `Config`, `ConfigurationManager`, `ConfigurationSource`, `ConfigurationValidator` |
| `constants.py` | Project-wide constants | (module-level constants) |
| `device.py` | Device detection (CPU/CUDA) | `DeviceInfo` |
| `environment.py` | Environment introspection | `EnvironmentInfo` |
| `exceptions.py` | Exception hierarchy | `BusinessCardAIError` + 9 subclasses |
| `logger.py` | Logging setup | `ColoredFormatter`, `setup_logger`, `get_logger` |
| `paths.py` | Project path resolution | `Paths` |
| `timer.py` | Execution timing | `Timer`, `timer_context`, `timer_decorator` |
| `version.py` | Version info | `get_version`, `get_full_version`, `get_description` |

### 2. I/O Layer (`src/core/io/`)

| Module | Responsibility | Key Classes |
|--------|---------------|-------------|
| `cache_manager.py` | Multi-level caching (memory + disk) | `CacheManager`, `MemoryCache`, `DiskCache`, `CacheEntry`, `CacheStatistics` |
| `directory_manager.py` | Directory operations | `DirectoryManager` |
| `file_manager.py` | File operations | `FileManager` |
| `image_io.py` | Image reading/writing | `ImageIO` |
| `json_io.py` | JSON serialization | `JSONIO` |
| `yaml_io.py` | YAML serialization | `YAMLIO` |
| `temp_manager.py` | Temporary file/directory management | `TempManager` |

### 3. Runtime Layer (`src/core/runtime/`)

| Module | Responsibility | Key Classes |
|--------|---------------|-------------|
| `dependency_container.py` | DI container | `DependencyContainer`, `Lifetime`, `Registration` |
| `service_registry.py` | Name-based service registry | `ServiceRegistry` |
| `runtime_context.py` | Centralized runtime context | `RuntimeContext` |
| `performance_monitor.py` | Performance tracking | `PerformanceMonitor`, `PerformanceSnapshot` |
| `memory_monitor.py` | Memory monitoring | `MemoryMonitor`, `MemorySnapshot` |
| `gpu_monitor.py` | GPU monitoring | `GPUMonitor`, `GPUSnapshot` |
| `metrics.py` | Metrics collection | `Counter`, `Gauge`, `Histogram`, `Timer`, `MetricRegistry` |
| `health_check.py` | System health checks | `HealthCheck`, `HealthCheckResult`, `HealthStatus` |

---

## Design Patterns

| Pattern | Usage | Location |
|---------|-------|----------|
| Singleton | Config class | `config.py` |
| Factory | DependencyContainer lifecycle | `dependency_container.py` |
| Registry | ServiceRegistry | `service_registry.py` |
| Observer | Performance monitor windowing | `performance_monitor.py` |
| Strategy | Configuration sources | `config.py` (YamlConfigurationSource, JsonConfigurationSource) |
| Template Method | Health checks | `health_check.py` |
| Composite | MetricRegistry | `metrics.py` |
| Facade | RuntimeContext | `runtime_context.py` |

---

## Data Flow

### Configuration Loading
```
File System → YamlConfigurationSource/JsonConfigurationSource
Environment → EnvironmentConfigurationSource
                       ↓
            ConfigurationManager._deep_merge()
                       ↓
               Typed getters (get_string, etc.)
```

### Dependency Injection
```
register(type, lifetime) → Registration
resolve(type) → [Check circular deps] → [Check instances] → Factory/Instance
```

### Health Check
```
HealthCheck.run_all() → [cuda, disk, config, permissions, dataset, models, cache]
                              ↓
                    List[HealthCheckResult]
                              ↓
                    HealthCheck.summary
```

---

## Dependency Graph

```
constants.py ─────────────────────────────────────┐
exceptions.py ───────────────────────────────────┐│
paths.py ───────────────────────────────────────┐││
version.py → constants.py                      │││
device.py → torch                              │││
environment.py → torch                         │││
config.py → constants, exceptions, paths       │││
logger.py → constants, paths, rich            │││
timer.py → constants                          │││
                                                │││
io/                                             │││
├── cache_manager.py → exceptions              │││
├── directory_manager.py → exceptions          │││
├── file_manager.py → exceptions               │││
├── image_io.py → exceptions, cv2, numpy       │││
├── json_io.py → exceptions                    │││
├── yaml_io.py → exceptions, yaml              │││
└── temp_manager.py                             │││
                                                │││
runtime/                                        │││
├── dependency_container.py → exceptions       │││
├── service_registry.py → exceptions           │││
├── runtime_context.py → config, device,       │││
│   environment, cache_manager, logger,        │││
│   paths, version ────────────────────────────┘││
├── memory_monitor.py → psutil                 ││
├── gpu_monitor.py → torch                     ││
├── performance_monitor.py → memory_monitor,   ││
│   gpu_monitor                                ││
├── metrics.py → json, threading, time         ││
└── health_check.py → config, paths, torch ────┘│
                                                 ▼
                                          No circular
                                          dependencies
```

---

## Public API Surface

### `src.core` (54 exports)
All major classes, functions, and constants from Config, ConfigurationManager, DeviceInfo, EnvironmentInfo, Paths, Timer, exceptions, version, constants.

### `src.core.io` (13 exports)
CacheManager, CacheEntry, CacheStatistics, CachePolicy, CacheSerializer, MemoryCache, DiskCache, DirectoryManager, FileManager, ImageIO, JSONIO, TempManager, YAMLIO.

### `src.core.runtime` (19 exports)
DependencyContainer, ServiceRegistry, RuntimeContext, PerformanceMonitor, MemoryMonitor, GPUMonitor, HealthCheck, all metric types, all snapshot types, HealthStatus.

---

## Architecture Decisions

1. **Clean Architecture** — Strict layer separation prevents circular dependencies
2. **Singleton Config** — Lazy-loaded singleton for global configuration access
3. **Strategy Pattern for Sources** — YAML, JSON, Environment sources are interchangeable
4. **RLock for Histogram** — Reentrant lock prevents deadlock when to_dict() calls internal properties
5. **NumPy optional in image_io.py** — Only imported when needed to keep memory footprint low
6. **psutil for monitoring** — Cross-platform process monitoring instead of platform-specific APIs
