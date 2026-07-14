# Data Augmentation Pipeline

Production-grade data augmentation pipeline for Business Card Detection — applies configurable chains of geometric and photometric transformations with deterministic reproducibility.

## Modules

### AugmentationConfig

Central configuration for all augmentation types, loaded from dict, YAML, or defaults.

```python
from src.augmentation import AugmentationConfig, DEFAULT_CONFIG

config = AugmentationConfig()
config = AugmentationConfig.from_dict({"rotation": {"enabled": False}})
config = AugmentationConfig.from_yaml("config.yaml")

config.disable_all()
config.enable_all()
config.is_enabled("rotation")  # True/False
config.to_dict()               # full config dict
```

Default config enables all 7 augmentations with moderate ranges and 0.3–0.5 probability.

### RotationAugmentation

Random or fixed-angle rotation with automatic canvas expansion.

```python
from src.augmentation import RotationAugmentation

aug = RotationAugmentation({
    "enabled": True,
    "probability": 1.0,
    "angle_range": [-30, 30],      # random angle range
    "fixed_angle": 90,             # or use fixed angle (None = random)
})
result = aug.apply(image, seed=42)
```

Supports grayscale images. When `angle_range[0] == angle_range[1]`, uses fixed angle.

### PerspectiveAugmentation

4-point random perspective warp controlled by strength factor.

```python
from src.augmentation import PerspectiveAugmentation

aug = PerspectiveAugmentation({
    "enabled": True,
    "probability": 1.0,
    "strength": 0.05,  # 0.0–1.0; higher = more distortion
})
result = aug.apply(image, seed=42)
```

At `strength=0.0`, the image is unchanged (identity warp). At `strength=1.0`, extreme distortion.

### LightingAugmentation

Adjusts brightness (scale), gamma correction, and exposure (HSV V-channel).

```python
from src.augmentation import LightingAugmentation

aug = LightingAugmentation({
    "enabled": True,
    "probability": 1.0,
    "brightness_range": [0.8, 1.2],  # multiplicative factor per pixel
    "gamma_range": [0.8, 1.2],       # gamma correction
    "exposure_range": [0.9, 1.1],    # HSV V-channel multiplier
})
result = aug.apply(image, seed=42)
```

### ContrastAugmentation

Alpha/beta contrast adjustment with optional histogram equalization.

```python
from src.augmentation import ContrastAugmentation

aug = ContrastAugmentation({
    "enabled": True,
    "probability": 1.0,
    "alpha_range": [0.8, 1.2],       # contrast factor
    "histogram_equalization": False,  # applies CLAHE-like equalization
})
result = aug.apply(image, seed=42)
```

Histogram equalization works on both RGB and grayscale inputs.

### BlurAugmentation

Gaussian blur (kernel-based) or motion blur (line kernel at random angle).

```python
from src.augmentation import BlurAugmentation

aug = BlurAugmentation({
    "enabled": True,
    "probability": 1.0,
    "gaussian_kernel_range": [3, 7],
    "motion_blur_kernel_range": [5, 15],
})
result = aug.apply(image, seed=42)
```

Randomly chooses gaussian or motion blur each call (50/50 split).

### NoiseAugmentation

Gaussian noise (additive) or salt & pepper noise (pixel replacement).

```python
from src.augmentation import NoiseAugmentation

aug = NoiseAugmentation({
    "enabled": True,
    "probability": 1.0,
    "gaussian_std_range": [0.01, 0.03],       # std as fraction of 255
    "salt_pepper_amount_range": [0.01, 0.03],  # fraction of pixels affected
})
result = aug.apply(image, seed=42)
```

Randomly chooses gaussian or salt & pepper each call (50/50 split). Output is clamped to [0, 255].

### ColorAugmentation

Saturation shift, hue rotation, and per-channel white balance adjustment.

```python
from src.augmentation import ColorAugmentation

aug = ColorAugmentation({
    "enabled": True,
    "probability": 1.0,
    "saturation_range": [0.8, 1.2],
    "hue_range": [-10, 10],          # degrees
    "white_balance_range": [0.9, 1.1],
})
result = aug.apply(image, seed=42)
```

Operates in HSV color space on RGB inputs. Grayscale images are returned unchanged.

### AugmentationPipeline

Chains multiple augmentations in configurable order with deterministic seed handling and change tracking.

```python
from src.augmentation import AugmentationPipeline, AugmentationConfig

config = AugmentationConfig()
pipeline = AugmentationPipeline(config)

result = pipeline.process(image, seed=42)
result.image                 # augmented ndarray
result.applied_transforms    # list of transformation names that changed the image
result.processing_time       # elapsed seconds
result.original_shape        # input shape
result.final_shape           # output shape

pipeline.set_order(["rotation", "contrast", "blur"])
pipeline.disable("noise")
pipeline.enable("noise")
pipeline.enabled_count       # number of currently enabled augmentations
```

Augmentations that don't change the image (e.g., blur on a uniform image) are not added to `applied_transforms`.

### AugmentationSession

High-level session for batch processing images from disk with statistics tracking.

```python
from src.augmentation import AugmentationSession, AugmentationPipeline

pipeline = AugmentationPipeline(config)
session = AugmentationSession(pipeline, output_dir="augmented/")

result = session.process_image("input.jpg", output_filename="out.jpg", seed=42)
result.image      # augmented image
result.applied_transforms  # list of applied transforms

results = session.process_batch(["img1.jpg", "img2.jpg"], seed=42)

stats = session.get_statistics()
stats.total_images
stats.total_augmented
stats.total_skipped
stats.total_failures
stats.total_time
stats.avg_time_per_image
stats.transform_counts  # {transform_name: count}
```

## Data Flow

```
Input Image (ndarray or file path)
     |
     v
AugmentationPipeline.process()
     |
     +-- rotation       (cv2.warpAffine, expand)
     +-- perspective    (cv2.warpPerspective)
     +-- lighting       (brightness × gamma × HSV exposure)
     +-- contrast       (alpha/beta + optional histogram eq)
     +-- blur           (gaussian or motion blur)
     +-- noise          (gaussian additive or salt & pepper)
     +-- color          (saturation × hue × white balance)
     |
     v
PipelineResult(image, applied_transforms, processing_time)
```

## Seed-Based Determinism

All augmentations support deterministic reproducibility via seed:

```python
# Same seed → same result
r1 = pipeline.process(image, seed=42)
r2 = pipeline.process(image, seed=42)
assert (r1.image == r2.image).all()
```

Each augmentation in the chain receives a unique sub-seed (`seed + position_index`) to prevent correlated random sequences across augmentation types.

## Config Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `seed` | `int | None` | `None` | Global seed override |
| `rotation.enabled` | `bool` | `True` | |
| `rotation.angle_range` | `[float, float]` | `[-15, 15]` | Degrees |
| `rotation.fixed_angle` | `float | None` | `None` | Overrides random if set |
| `rotation.probability` | `float` | `0.5` | |
| `perspective.enabled` | `bool` | `True` | |
| `perspective.strength` | `float` | `0.05` | 0.0–1.0 |
| `perspective.probability` | `float` | `0.5` | |
| `lighting.enabled` | `bool` | `True` | |
| `lighting.brightness_range` | `[float, float]` | `[0.8, 1.2]` | |
| `lighting.gamma_range` | `[float, float]` | `[0.8, 1.2]` | |
| `lighting.exposure_range` | `[float, float]` | `[0.9, 1.1]` | HSV V-channel |
| `lighting.probability` | `float` | `0.5` | |
| `contrast.enabled` | `bool` | `True` | |
| `contrast.alpha_range` | `[float, float]` | `[0.8, 1.2]` | |
| `contrast.histogram_equalization` | `bool` | `False` | |
| `contrast.probability` | `float` | `0.5` | |
| `blur.enabled` | `bool` | `True` | |
| `blur.gaussian_kernel_range` | `[int, int]` | `[3, 7]` | Odd kernel sizes |
| `blur.motion_blur_kernel_range` | `[int, int]` | `[5, 15]` | Odd kernel sizes |
| `blur.probability` | `float` | `0.3` | |
| `noise.enabled` | `bool` | `True` | |
| `noise.gaussian_std_range` | `[float, float]` | `[0.01, 0.03]` | As fraction of 255 |
| `noise.salt_pepper_amount_range` | `[float, float]` | `[0.01, 0.03]` | Fraction of pixels |
| `noise.probability` | `float` | `0.3` | |
| `color.enabled` | `bool` | `True` | |
| `color.saturation_range` | `[float, float]` | `[0.8, 1.2]` | |
| `color.hue_range` | `[int, int]` | `[-10, 10]` | Degrees |
| `color.white_balance_range` | `[float, float]` | `[0.9, 1.1]` | Per-channel |
| `color.probability` | `float` | `0.5` | |
