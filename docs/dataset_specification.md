# Dataset Specification

## Overview

This document defines the complete specification for the Business Card Detection dataset used in the Business Card AI system.

### Purpose

The dataset serves as the foundation for training a detection model to locate business cards within images. The detected card region is then used by downstream OCR and classification modules.

### Scope

- Raw image collection
- Annotation rules
- Preprocessing requirements
- Quality standards
- Lifecycle management

---

## 1. Dataset Folder Structure

```
dataset/
├── raw/
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── val/
│   │   ├── images/
│   │   └── labels/
│   └── test/
│       ├── images/
│       └── labels/
├── intermediate/
│   ├── augmented/
│   ├── preprocessed/
│   └── deduplicated/
├── final/
│   ├── train/
│   │   ├── images/
│   │   └── labels/
│   ├── val/
│   │   ├── images/
│   │   └── labels/
│   └── test/
│       ├── images/
│       └── labels/
├── annotations/
│   ├── originals/
│   └── corrections/
├── metadata/
│   ├── images.csv
│   ├── splits.csv
│   └── issues.csv
├── exports/
│   ├── yolo/
│   ├── coco/
│   └── tfrecord/
├── processed/     (deprecated)
├── raw/           (deprecated)
├── labels/        (deprecated)
└── augmented/     (deprecated)
```

### Directory description

| Directory | Purpose | Git-friendly |
|-----------|---------|--------------|
| `raw/train|val|test/` | Original unmodified images + YOLO labels | Yes |
| `intermediate/augmented/` | Augmented copies and label files | No |
| `intermediate/preprocessed/` | Resized, normalized versions | No |
| `intermediate/deduplicated/` | Near-duplicate free images | No |
| `final/train|val|test/` | Production-ready curated dataset | No |
| `annotations/originals/` | Original annotation files (VOC, COCO, CSV) | No |
| `annotations/corrections/` | Manually corrected annotation logs | No |
| `metadata/` | Structured info about each image | No |
| `exports/yolo/` | YOLO format export | No |
| `exports/coco/` | COCO JSON format export | No |
| `exports/tfrecord/` | tfrecord format export | No |

### Directory placement rule

- **Git-friendly**: Allowed to be tracked in git (small, static)
- **Not Git-friendly**: excluded via `.gitignore` (large, or generated)

---

## 2. Image requirements

### Supported formats

| Format | Extension | MIME type |
|--------|-----------|-----------|
| JPEG | `.jpg` `.jpeg` | `image/jpeg` |
| PNG | `.png` | `image/png` |
| BMP | `.bmp` | `image/bmp` |
| WebP | `.webp` | `image/webp` | 
| TIFF (single page) | `.tiff` `.tif` | `image/tiff` |

### Image requirements

| Property | Minimum | Maximum | Recommended |
|----------|---------|---------|-------------|
| Height | 320 px | 4096 px | 1080 px |
| Width | 320 px | 4096 px | 1920 px |
| Total megapixels | 0.1 | 12 | 2-4 |
| File size | 10 KB | 10 MB | 200-500 KB |

### Aspect ratio rules

- Any aspect ratio allowed **provided resolution is in range**.
- Cards must occupy at least 5% of total image pixels.
- Violating images should be cropped to a Region of Interest prior to addition.

### Compression rules

- JPEG compression is allowed for all training images.
- Maximum compression level: JPEG quality 85% (Q=85).
- PNG is strongly preferred for images that will be further augmented.
- WebP is acceptable at compression 90 or higher.
- Never use interlaced/Progressive JPEG.

---

## 3. Object class definitions

### Core classes

| ID | Name | Color | Description |
|----|------|-------|-------------|
| 0 | `business_card` | `#00FF00` (Green) | Any business card |

### Future expansion classes

| ID | Name | Color | Description |
|----|------|-------|-------------|
| 1 | `qr_code` | `#FF0000` (Red) | QR Code / Barcode present on the card |
| 2 | `logo` | `#0000FF` (Blue) | Company name or logo present on card |
| 3 | `photo` | `#FF00FF` (Magenta) | Person photo present on the card |
| 4 | `nfc_marker` | `#FFFF00` (Yellow) | NFC chip icon or text indicator |

### Class inheritance rule

- For Version 1.0 only class 0 (business_card) is active.
- Future classes must not interfere with the bounding box of class 0.
- For example, a logo is always a subregion inside the business_card bounding box.

### reserved IDs

| ID | Name | Description |
|----|------|-------------|
| 5–999 | Reserved | Reserved for future class definitions |

---

## 4. Annotation rules

### General annotation policy

- all annotations must be in YOLO format:
  ```
  class_id x_center y_center width height
  ```
- x_center, y_center, width, height are normalized to [0, 1].
- YOLO uses top-left image origin, x-axis pointing right, y-axis pointing down.
- each image file must have an accompanying `.txt` file with the same name.

### 4.1 Bounding box policy

- use axis-aligned bounding boxes.
- the box must tightly enclose the visible card region.
- box must be inside the image boundaries.
- zero-area boxes are prohibited.
- box width and height must each be >= 1% of the respective image dimension.
- Box center must be inside the image.

### 4.2 Occluded cards

- Annotate only the visible portion of the card.
- If > 70% of the card is occluded, do not annotate.
- If 30–70% is occluded, annotate the visible region and quality-score the image low.
- If < 30% is occluded, annotate as normal.

### 4.3 Rotated cards

- Use axis-aligned bounding box that fully contains the rotated card.
- The box may have area larger than the card, but must not include another card.
- The cardinal point location on the card (top-left, top-right, etc.) may be stored as optional metadata.

### 4.4 Multiple cards

- Annotate all cards in an image individually.
- Each card gets its own bounding box.
- Overlapping boxes are allowed if cards physically overlap.
- Extremely small cards (<1% of image pixels) must be removed.

### 4.5 Blurred cards

- All visible cards must be annotated.
- Heavily blurred cards (> 50% of card pixels with visible motion blur) should be quality-scored low.
- Completely unrecognizable cards (cannot tell if object is a business card) must not be annotated.

### 4.6 Shadow

- Annotate the actual card shape, not the shadow.
- If shadow merges two cards, annotate each card separately.
- Drop shadow on a table is ignored.

### 4.7 Reflection / glare

- Annotate the full card extent despite reflections.
- If glare covers > 60% of the card surface, score the image low.
- Reflectance on glass or mirrors which duplicates the card should not be annotated.

### 4.8 Perspective / skew

- Bounding box must enclose the entire card as it appears.
- If the card is under extreme perspective (one side less than 20% of the opposite side), score the image low.
- Perspective distortion of up to 45 degrees along each axis is allowed.

### 4.9 Cut edges / truncation

- Annotate the visible portion of the card.
- If more than 50% of the card is truncated by the image edge, do not annotate.
- If 25-50% is truncated, annotate and score the image low.
- If less than 25% is truncated, annotate as normal.

### annotation format details

```
<object_class_id> <x_center> <y_center> <width> <height>
```

Where:
- `object_class_id`: integer in [0, 4] as defined above.
- `x_center`: float between 0 and 1 representing the center of bounding box relative to image width.
- `y_center`: float between 0 and 1 representing the center of bounding box relative to image height.
- `width`: float between 0 and 1 representing the width of bounding box relative to image width.
- `height`: float between 0 and 1 representing the height of bounding box relative to image height.

### Quality scoring of images

Each image may optionally have a quality score:

| Score | Criteria |
|-------|----------|
| 3 | clear, front-facing, good lighting, no artifact |
| 2 | minor blur/rotation/truncation |
| 1 | severe blur/occlusion/rotation/perspective, barely annotatable |
| 0 | do not include |

---

## 5. Dataset split

### Recommended percentages

| Split | Ratio | Image count (minimum) | Purpose |
|-------|-------|-----------------------|---------|
| Train | 70% | 490 | Model weight training |
| Validation | 15% | 105 | Early stopping and hyper-parameter tuning |
| Test | 15% | 105 | Final model evaluation |

### Minimum viable volumes

| Target | Train | Val | Total |
|--------|-------|-----|-------|
| MVP (Minimum viable product) | 200 | 50 | 300 |
| Baseline | 500 | 100 | 700 |
| Production | 3500 | 750 | 5000 |
| Target | 7000 | 1500 | 10000 |

### Split constraints

- Images from the same source location or the same recording session must be kept within the same split.
- Splits must be stratified: all card orientations must be represented in all three splits.
- Set seed for reproducibility: `BCA_SEED = 42`
- Use file-based hashing to ensure images are not reused across splits.

---

## 6. Naming convention

### Image files

```
BCA001_001_V1-0.jpg
 ^     ^   ^
 │     │   └─ version: V{major}-{minor}
 │     └───── image number: {3-digit zero padded}
 └─────────── batch code: BCA + {3-digit zero padded batch}
```

Examples:
- `BCA001_001_V1-0.jpg`
- `DRC_BCA001_002_V1-0.png`
- Traceability: use original filename prefix.

### Label files

```
BCA001_001_V1-0.txt
```

Always matches the base name of the corresponding image.

### Batch versioning

Batch codes:
- BCA001, BCA002, ..., BCA999
- DRC: don’t run & collect
- WEB: web scrape

### Version numbers

| Version | Class IDs | Status |
|---------|-----------|--------|
| V1-0 | 0 | MVP release |
| V1-1 | 0 | Quality improvements |
| V2-0 | 0, 1 | QR code added |
| V2-1 | 0, 1, 2 | Logo added |
| V3-0 | 0-4 | All classes |

### File naming rules

- No spaces allowed.
- Use only alphanumeric, underscore, hyphen and period.
- Maximum filename length: 255 bytes.
- Labels and corresponding images must have the same base name.
- Labels must use `.txt` extension.

---

## 7. Quality checklist

### Image level

- [ ] No corrupted files
- [ ] All images readable by cv2
- [ ] Minimum resolution of 320x320
- [ ] File size within 10 KB to 10 MB
- [ ] Aspect ratio causes floating point representation to fit within normalized coordinates
- [ ] Not a duplicate (SHA256 comparison)
- [ ] Not a near-duplicate (average hash, correlation score < 0.9)
- [ ] No watermark overlays
- [ ] No solid color / no content images
- [ ] No screenshots of a screen (secondary capture)

### Annotation level

- [ ] All raw images have a matching label file
- [ ] All labels are valid YOLO format
- [ ] No class ID out of range for the version
- [ ] x_center is in [0, 1]
- [ ] y_center is in [0, 1]
- [ ] width is > 0 and <= 1
- [ ] height is > 0 and <= 1
- [ ] width * image_width >= 0.01 * image_width (1% minimum)
- [ ] height * image_height >= 0.01 * image_height (1% minimum)
- [ ] bounding box fits entirely within image (x_center +- width/2)
- [ ] No duplicate annotations (same class with overlapping boxes)
- [ ] No annotations on images that were scored 0
- [ ] At least one annotation per image

### Sampling quality

- [ ] At least 10% of images contain 3+ cards (multiple per image)
- [ ] At least 10% of total cards are heavily rotated (>45 degrees)
- [ ] At least 10% of total images have occluded/blur cards (challenging)
- [ ] At least 10% of total images contain at least 2 color tone variations (warm, cool)
- [ ] Background scenario diversity: office, home, outdoors, vehicles
- [ ] Surface diversity: wood, plastic, glass, paper, fabric
- [ ] Lighting diversity: direct sunlight, cloudy, fluorescent, tungsten, twilight, shadow

### Cross-split charges

- [ ] No image duplication across splits
- [ ] No near-duplicate pairing across splits
- [ ] Distribution of the number of cards per image similar across splits
- [ ] Distribution of card areas similar across splits

---

## 8. Acceptance criteria

### For Dataset V1-0 (MVP)

- [ ] Minimum of 300 raw images (train+val) collected
- [ ] Minimum of 150 images annotated (train)
- [ ] All annotations reviewed by human
- [ ] At least 30 images for validation
- [ ] All annotation files conform to YOLO format
- [ ] All images conform to minimum requirements
- [ ] Average quality score >= 2.0
- [ ] At least 3 different sources of data
- [ ] At least 10% variation in card angles
- [ ] At least 5% variation in lighting
- [ ] less than 1% corrupt/malformed files discovered during validation
- [ ] Annotators have demonstrated < 2% margin of error on a batch test

### For Dataset V2-0

- [ ] 700 total images annotated (500+ train)
- [ ] QR code detection supported
- [ ] 5 sources of images minimum
- [ ] 20% extreme angles or artifacts (quality score == 1)
- [ ] less than 1% annotation error (pre-correction)
- [ ] less than 0.1% conversion/corruption errors (post-correction)

### For Dataset V3-0

- [ ] 5000 images minimum
- [ ] All 5 class IDs supported
- [ ] At least 10 different sources
- [ ] less than 0.5% error after correction
- [ ] Automatic validation pass rate > 90%

---

## 9. Future dataset roadmap

### Phase 1 - Raw Collection (current)

- Collect raw images from diverse sources:
  - Office environments
  - Conferences and networking events
  - Home offices
  - Outdoor settings
  - Professional photo shoots (green background)
- Min image resolution: 640x480
- Sources: internal collection, contractors, Privacy-compliant open sources

### Phase 2 - Annotation

- Annotate all collected images
- Use YOLO format as primary annotation standard
- Secondary annotation conversion: COCO, tfrecord.

### Phase 3 - Augmentation and balancing

- Apply standard augmentations:
  - Random rotation (±45 degrees)
  - Random scaling (0.8× to 1.2×)
  - Gaussian blur
  - Brightness and color jitter
  - Cutout / random erasing
  - Mixup augmentation
  - mosaic augmentation
  - copy-paste augmentation

### Phase 4 - Quality review

- Visual inspection of all annotations
- Cross-annotator consistency check (if multiple)
- Near-duplicate removal
- Statistical analysis of label distribution

### Future expansions

- Privacy-compliant augmentation from synthetic card generation
- Active learning: hardest-case re-annotation cycles
- Multi-class expansion (QR, logo, etc.)
- Real-time collection via annotation pipeline

---

## Appendix

### A. YOLO annotation example

Image: `BCA001_001_V1-0.jpg` (1920x1080)
Card center at (960, 540) with size 800x600:

```
0 0.500 0.500 0.416 0.555
```

### B. References

- YOLO format: https://www.v7labs.com/blog/yolo-object-detection
- COCO format: https://cocodataset.org/#format-data
- tfrecord format: https://www.tensorflow.org/tutorials/load_data/tfrecord

### C. Terms

| Term | Definition |
|------|------------|
| card | a physical business card object |
| annotation | YOLO-format label attached to an image |
| RAW | Original unmodified image file |
| AUGMENTED | image that has been programmatically modified |
| BATCH | A group of images sharing a source and date |
| SCORE | Per-image quality score: 0-3 |
| near-duplicate | images with average hash correlation >= 0.9 |
