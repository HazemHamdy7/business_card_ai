# Runtime Layer

## Overview

The Runtime layer provides the infrastructure backbone for the Business Card AI system. It includes dependency injection, service registry, runtime context, performance monitoring, metrics collection, and health checks.

## Modules

### DependencyContainer (`src/core/runtime/dependency_container.py`)

A dependency injection container supporting multiple lifetimes:

- **Singleton** - One instance per container, created eagerly or via instance
- **Lazy Singleton** - One instance per container, created on first resolve
- **Transient** - New instance every resolve
- **Factory** - Custom factory function per resolve

**Features:**
- Resolve by Type
- Resolve by Name
- Auto-registration from modules
- Auto-wiring via constructor parameter inspection
- Circular dependency detection
- Child containers
- Thread-safe registration and resolution

```python
container = DependencyContainer()
container.register_singleton(MyService)
container.register_transient(OtherService, name="custom")
instance = container.resolve(MyService)
named = container.resolve(OtherService, name="custom")
```

### ServiceRegistry (`src/core/runtime/service_registry.py`)

A lightweight name-based service registry for services not requiring DI.

```python
registry = ServiceRegistry()
registry.register("db", db_service)
service = registry.get("db")
```

### RuntimeContext (`src/core/runtime/runtime_context.py`)

Central context aggregating all core services:

- ConfigurationManager
- Logger
- DeviceInfo
- EnvironmentInfo
- CacheManager
- Project Paths
- Version

```python
ctx = RuntimeContext()
ctx.initialize()
device = ctx.device
config = ctx.config
```

### PerformanceMonitor (`src/core/runtime/performance_monitor.py`)

Tracks execution performance metrics:
- Execution time (avg, min, max)
- Memory usage (RSS in MB)
- CPU utilization
- GPU utilization
- FPS

Window-based sampling with configurable window size.

### MemoryMonitor (`src/core/runtime/memory_monitor.py`)

Process-level memory monitoring using psutil:
- RSS memory (MB)
- VMS memory (MB)
- Memory percent
- CPU percent
- System available/total memory

### GPUMonitor (`src/core/runtime/gpu_monitor.py`)

CUDA GPU monitoring:
- GPU utilization percent
- Memory used/free/total (MB)
- Device name
- Graceful fallback when CUDA unavailable

### Metrics (`src/core/runtime/metrics.py`)

Metric types:
- **Counter** - Increment/decrement counter
- **Gauge** - Float value that can be set/inc/dec
- **Histogram** - Value distribution with configurable buckets
- **Timer** - Duration tracking with histogram

`MetricRegistry` manages named metrics and supports JSON export.

### HealthCheck (`src/core/runtime/health_check.py`)

Verifies system health across:
- CUDA availability
- Disk space
- Configuration integrity
- Write permissions
- Dataset directory
- Models directory
- Cache directory

```python
health = HealthCheck()
results = health.run_all()
summary = health.summary
```

## Exception Classes

| Exception | Description |
|-----------|-------------|
| CircularDependencyError | Circular dependency detected in DI |
| ServiceNotFoundError | Service not registered |
| RegistrationError | Service registration failure |
| HealthCheckError | Health check failure |
| ResourceExhaustedError | Resource limit reached |

## Testing

- Unit tests: tests/unit/core/runtime/
- Integration tests: tests/integration/core/runtime/
- Stress tests: tests/stress/core/runtime/
- Benchmark tests: tests/benchmark/core/runtime/
