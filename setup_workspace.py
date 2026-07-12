from pathlib import Path

ROOT = Path(__file__).parent

directories = [
    "src",
    "src/api",
    "src/cli",
    "src/core",
    "src/preprocessing",
    "src/detection",
    "src/ocr",
    "src/classification",
    "src/postprocessing",
    "src/training",
    "src/evaluation",
    "src/inference",
    "src/exporters",
    "src/utils",

    "tests",
    "tests/unit",
    "tests/integration",
    "tests/benchmark",
    "tests/stress",

    "config",

    "dataset",
    "dataset/raw",
    "dataset/processed",
    "dataset/annotations",
    "dataset/exports",

    "models",
    "models/checkpoints",
    "models/pretrained",
    "models/onnx",

    "docs",

    "logs",

    "tools",
]

files = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    ".env",
    ".env.example",
    "pyproject.toml",

    "src/__init__.py",

    "src/core/__init__.py",
    "src/core/config.py",
    "src/core/logger.py",
    "src/core/constants.py",
    "src/core/device.py",
    "src/core/exceptions.py",

    "src/api/__init__.py",

    "src/cli/__init__.py",

    "src/preprocessing/__init__.py",

    "src/detection/__init__.py",

    "src/ocr/__init__.py",

    "src/classification/__init__.py",

    "src/postprocessing/__init__.py",

    "src/training/__init__.py",

    "src/evaluation/__init__.py",

    "src/inference/__init__.py",

    "src/exporters/__init__.py",

    "src/utils/__init__.py",
]

for directory in directories:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

for file in files:
    path = ROOT / file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print("=" * 60)
print("Business Card AI Workspace Created Successfully")
print("=" * 60)