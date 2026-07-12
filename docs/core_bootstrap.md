# Core Bootstrap

## Overview

The `src/core/` package provides the foundational infrastructure for all Business Card AI modules. It contains no AI logic, no OCR, no YOLO, no ONNX — only reusable bootstrap utilities.

## Modules

| Module        | File              | Purpose                                    |
|---------------|-------------------|--------------------------------------------|
| Constants     | `constants.py`    | Project-wide constants and magic numbers   |
| Paths         | `paths.py`        | Project root detection and path management |
| Exceptions    | `exceptions.py`   | Exception hierarchy                        |
| Device        | `device.py`       | Hardware detection (CPU/CUDA)              |
| Environment   | `environment.py`  | System environment introspection           |
| Logger        | `logger.py`       | Colored console + rotating file logging     |
| Config        | `config.py`       | YAML config loader and environment loader  |
| Timer         | `timer.py`        | Context manager, decorator, stopwatch      |
| Version       | `version.py`      | Project version helpers                    |

## Architecture

All modules follow Single Responsibility Principle. No module depends on AI libraries. The `Paths` class uses marker files (`.git`, `pyproject.toml`, `AGENTS.md`) to detect the project root dynamically — no hardcoded paths anywhere.

## Usage

```python
from src.core import Paths, Config, setup_logger, get_device, Timer

# Paths
root = Paths.root()
Paths.ensure_dirs()

# Config
config = Config()
config.load()
config.set("model.type", "yolo")

# Logger
logger = setup_logger("my_module")
logger.info("Ready")
logger.success("Done")

# Device
device = get_device()
print(device.device_type)

# Timer
with timer_context("operation"):
    do_work()
```

## Dependencies

- Python 3.11+
- PyTorch (for device/environment detection)
- PyYAML (for config)
- Rich (for colored logging)
