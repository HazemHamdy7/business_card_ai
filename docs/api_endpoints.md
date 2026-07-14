# API Reference — Business Card AI

Base URL: `http://localhost:8000`

## Endpoints

### `GET /`
Root API information.

**Response 200:**
```json
{
  "status": "running",
  "title": "Business Card AI API",
  "version": "0.1.0",
  "api_version": "v1",
  "description": "..."
}
```

### `GET /health`
System health check.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "python_version": "3.11.9",
  "gpu_available": true,
  "cuda_available": true,
  "memory_usage": { "rss_mb": 150.5, ... },
  "disk_usage": { "total_gb": 256.0, ... },
  "uptime": "123.45s"
}
```

### `GET /version`
Version information.

**Response 200:**
```json
{
  "version": "0.1.0",
  "api_version": "v1",
  "title": "Business Card AI API",
  "description": "..."
}
```

### `GET /system`
System information.

**Response 200:**
```json
{
  "python_version": "3.11.9",
  "platform": "Windows-10-...",
  "cpu_count": 8,
  "memory": { ... },
  "environment": "development"
}
```

### `GET /dataset/status`
Dataset quality and readiness status.

**Parameters:**
- `dataset_root` (query, optional): Path to dataset root directory

**Response 200:**
```json
{
  "ready": true,
  "quality_score": 85.5,
  "total_images": 100,
  "total_labels": 3,
  "num_classes": 5,
  "total_objects": 200,
  "imbalance_score": 0.3
}
```

### `GET /annotation/status`
Annotation validation status.

**Parameters:**
- `label_dir` (query, optional): Path to label directory

**Response 200:**
```json
{
  "ready": true,
  "total_files": 50,
  "total_objects": 150,
  "valid_files": 48,
  "invalid_files": 2
}
```

### `POST /predict` *(Not Implemented)*
Submit an image for prediction.

**Request:**
```json
{
  "image": "base64encodedstring",
  "options": { "model": "v1" }
}
```

**Response 501:**
```json
{
  "success": false,
  "message": "Prediction pipeline is not implemented yet.",
  "predictions": []
}
```

### `POST /detect` *(Not Implemented)*
Object detection.

**Response 501**

### `POST /ocr` *(Not Implemented)*
Optical character recognition.

**Response 501**

### `POST /business-card` *(Not Implemented)*
Full business card processing pipeline.

**Response 501**

## Error Responses

All errors return JSON:
```json
{
  "success": false,
  "message": "Error description",
  "status_code": 404,
  "timestamp": "2026-07-15T00:00:00"
}
```

## Headers
All responses include:
- `X-Request-ID` — Unique request identifier
- `X-Execution-Time` — Server-side processing time
- Standard CORS headers

## Interactive Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
