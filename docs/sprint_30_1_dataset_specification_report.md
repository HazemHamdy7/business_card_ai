# Sprint 30.1 — Dataset Specification

## Execution Report

**Date:** 2026-07-13
**Branch:** feature/sprint-30-1-dataset-specification
**Type:** Documentation only
**Status:** Complete

---

## Summary

Created the complete dataset specification for Business Card Detection. This document defines all rules, formats, and quality standards for building the training dataset. It does not implement any AI, train any models, or install any libraries.

---

## Deliverables

| File | Description |
|------|-------------|
| `docs/dataset_specification.md` | Complete dataset specification |
| `docs/sprint_30_1_dataset_specification_report.md` | This report |

---

## Specification sections

| Section | Description |
|---------|-------------|
| 1. Folder Structure | Complete dataset directory layout with raw/intermediate/final/metadata/exports |
| 2. Image requirements | Supported formats, resolution bounds, aspect ratio, compression rules |
| 3. Class definitions | Class 0: business_card, future classes 1-4: qr_code, logo, photo, nfc_marker |
| 4. Annotation rules | Bounding box policy, occluded/rotated/multiple/blurred/shadow/reflection/perspective/truncated |
| 5. Dataset split | Train 70% / Val 15% / Test 15% with minimum viable volumes |
| 6. Naming convention | Batch codes, image/label filenames, version numbering |
| 7. Quality checklist | Image-level, annotation-level, sampling-quality, cross-split checks |
| 8. Acceptance criteria | V1-0 MVP, V2-0, V3-0 criteria with pass/fail conditions |
| 9. Future roadmap | 4-phase plan: collection, annotation, augmentation, quality review |

---

## Specification details

### Folder structure

- **3-tier**: raw → intermediate → final
- **raw/**: original images + YOLO labels (git-friendly)
- **intermediate/**: augmented, preprocessed, deduplicated (git-ignored)
- **final/**: production-ready curated dataset (git-ignored)
- **metadata/**: structured CSV tracks per-image data
- **exports/**: yolo, coco, tfrecord format exports

### Image requirements

- Formats: JPEG, PNG, BMP, WebP, TIFF
- Min resol: 320×320, Max resol: 4096×4096
- Min area: 0.1 MP, Max area: 12 MP
- JPEG quality ≥ 85, no progressive JPEG

### Class definitions

- **V1.0**: class 0 `business_card` only
- **V2.0**: add `qr_code` (class 1)
- **V2.1**: add `logo` (class 2)
- **V3.0**: add `photo` (3), `nfc_marker` (4)

### Annotation rules

9 detailed annotation policies:
1. Bounding box — axis-aligned, tight, within-image
2. Occluded — annotate visible, skip >70% occluded
3. Rotated — full-enclosing axis-aligned box
4. Multiple — each card individually
5. Blurred — annotate all, score low if severe
6. Shadow — card shape only, not shadow
7. Reflection — full card extent despite glare
8. Perspective — full card, up to 45°
9. Cut edges — visible portion, skip >50% truncated

### Dataset splits

- 70/15/15 = Train/Val/Test
- MVP: 300 images min (200 train)
- Baseline: 700 images (500 train)
- Production: 5,000 images (3,500 train)
- Target: 10,000 images

### Quality checklist

28 quality checks across 4 categories (image, annotation, sampling, cross-split).

---

## Project status

| Component | Status |
|-----------|--------|
| Project initialization | Complete |
| Core infrastructure | Complete |
| Dataset specification | **Complete (this sprint)** |
| Data collection | Pending |
| Annotation | Pending |
| Augmentation pipeline | Pending |
| Detection training | Pending |

---

## Remaining work

1. **Data collection** — acquire raw images per specification
2. **Build annotation pipeline** — implement tools that enforce the specification
3. **Build validation tools** — automated checks for format, bounds, duplicates
4. **Augmentation scripts** — implement the augmentation phase
5. **Dataset curation** — review, correct, and finalize dataset
6. **Detection training** — train YOLO/detection model using the curated dataset

---

## No violations

| Rule | Status |
|------|--------|
| No AI implementation | ✅ |
| No model training | ✅ |
| No new library installation | ✅ |
| Documentation only | ✅ |
| Study of existing architecture | ✅ |
