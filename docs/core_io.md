# Core I/O Module Documentation

## Overview

The `src/core/io/` package provides the reusable I/O and file management layer for the Business Card AI project.

## Modules

| Module | File | Description |
|--------|------|-------------|
| FileManager | `file_manager.py` | Generic file read/write/copy/move/delete/rename operations |
| JSONIO | `json_io.py` | JSON file load/save |
| YAMLIO | `yaml_io.py` | YAML file load/save |
| ImageIO | `image_io.py` | Image read/write/resize/convert/validate |
| DirectoryManager | `directory_manager.py` | Directory create/delete/clean/tree/temp operations |
| TempManager | `temp_manager.py` | Temporary directory and file lifecycle management |
| CacheManager | `cache_manager.py` | Memory and disk cache with TTL support |

## Architecture

### CacheManager

The cache system is composed of the following classes:

- `CacheEntry` - Dataclass representing a single cache entry with key, value, timestamps, and size
- `CacheStatistics` - Dataclass tracking hits, misses, evictions, and storage usage
- `CachePolicy` - Dataclass defining default TTL and size limits
- `CacheSerializer` - Utility class for serializing/deserializing cache values
- `MemoryCache` - Thread-safe in-memory cache with TTL support and eviction policy
- `DiskCache` - On-disk cache using pickle serialization
- `CacheManager` - Unified orchestrator for memory and disk caching

### ConfigurationManager

The configuration system consists of:

- `ConfigurationSource` - Abstract base class for config sources
- `YamlConfigurationSource` - Loads configuration from YAML files
- `JsonConfigurationSource` - Loads configuration from JSON files
- `EnvironmentConfigurationSource` - Loads configuration from environment variables
- `ConfigurationValidator` - Validates configuration data and types
- `ConfigurationManager` - Coordinates sources with priority (env > file > defaults)

## Usage

### Cache
```python
from src.core.io import CacheManager, CachePolicy

policy = CachePolicy(default_ttl=300.0, max_memory_entries=1000)
cache = CacheManager(cache_dir=some_path, policy=policy)
cache.put("key", {"data": 42}, ttl=60.0)
value = cache.get("key")
stats = cache.stats
```

### Configuration
```python
from src.core.config import ConfigurationManager

cm = ConfigurationManager()
cm.load()
cm.set_defaults({"app": {"mode": "production"}})
mode = cm.get_string("app.mode")
count = cm.get_int("app.count", 10)
```

### Directory
```python
from src.core.io import DirectoryManager

DirectoryManager.create(tmp_path)
tree = DirectoryManager.tree(tmp_path)
```

### Image
```python
from src.core.io import ImageIO

img = ImageIO.read("image.jpg")
rgb = ImageIO.to_rgb(img)
ImageIO.write("output.jpg", rgb)
meta = ImageIO.metadata("image.jpg")
```

## Dependencies

- `PyYAML` (YAML config loading)
- `opencv-python` (ImageIO)
- `numpy` (Image representation)
