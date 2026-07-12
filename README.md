# Business Card AI

Offline AI-powered Business Card Recognition System.

## Goals

- Detect business cards from images
- Correct perspective
- Extract text using OCR
- Classify business card fields
- Train local AI models
- Export ONNX models
- Integrate with Flutter

## Project Structure

```
src/
tests/
dataset/
models/
docs/
config/
tools/
```

## Pipeline

```
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
ONNX Export
```

## Status

Project initialization completed.