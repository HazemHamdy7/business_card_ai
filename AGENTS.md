# Business Card AI - Project Rules

## Project Goal

Build a fully offline AI-powered Business Card Recognition System.

The final output is an ONNX model integrated into the Flutter application.

---

# Architecture

This project follows Clean Architecture.

Every feature must be reusable.

Never duplicate code.

Never create temporary solutions.

---

# Development Rules

- Never modify main directly.
- Every sprint starts from main.
- Every sprint uses its own feature branch.
- Merge only after:
  - All tests pass.
  - No analyzer issues.
  - Documentation updated.

---

# Coding Rules

- Python 3.11 only.
- Type hints required.
- Small reusable classes.
- Single Responsibility Principle.
- No magic numbers.
- Prefer composition over inheritance.
- Never hardcode paths.

---

# Testing Rules

Every sprint must include:

- Unit Tests
- Integration Tests
- Benchmark Tests
- Stress Tests

All tests must pass before merge.

---

# Documentation Rules

Every sprint generates:

docs/sprint_x_execution_report.md

Include:

- Files created
- Architecture
- LOC
- Tests
- Performance
- Limitations
- Future work

---

# AI Rules

Never fake AI.

Never fake accuracy.

Never fabricate predictions.

Unknown must remain Unknown.

Confidence must always be measurable.

---

# Pipeline

Image

↓

Card Detection

↓

Perspective Correction

↓

OCR

↓

OCR Recovery

↓

Classification

↓

Validation

↓

Business Card JSON

↓

Training Dataset

↓

Training

↓

ONNX Export

↓

Flutter Runtime

---

# Branch Strategy

main

feature/sprint-30-0-core

feature/sprint-30-1-card-detection

feature/sprint-30-2-dataset

feature/sprint-30-3-training

feature/sprint-30-4-ocr

feature/sprint-30-5-classification

feature/sprint-30-6-onnx

feature/sprint-30-7-flutter

Delete feature branches after merge.

---

# Quality

Code must always be production-ready.

No placeholders.

No duplicated utilities.

No dead code.