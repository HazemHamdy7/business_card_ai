# Development API — Sprint 30.7

## Overview
Production-ready REST API for Business Card AI built with FastAPI, Pydantic v2, and async endpoints. Provides health monitoring, dataset/annotation status, system info, and placeholder prediction endpoints.

## Architecture

```
src/api/
├── __init__.py           # Module exports
├── config.py             # APIConfig, Environment enum
├── logging.py            # StructuredFormatter, setup_logging, get_logger
├── version.py            # Version constants, get_version_info()
├── exceptions.py         # BusinessCardAIException hierarchy
├── response.py           # success_response(), error_response()
├── request_models.py     # Pydantic request models
├── response_models.py    # Pydantic response models
├── middleware.py         # RequestID, Logging, ExecutionTime, CORS, GZip
├── dependencies.py      # FastAPI dependency injection
├── health.py            # Health/system info gathering
├── app.py               # create_app() factory with lifespan
├── server.py            # run_server() uvicorn launcher
└── routes/
    ├── __init__.py      # Aggregated api_router
    ├── health_routes.py # GET /, /health, /version
    ├── system_routes.py # GET /system
    ├── dataset_routes.py# GET /dataset/status
    ├── annotation_routes.py # GET /annotation/status
    └── prediction_routes.py # POST /predict, /detect, /ocr, /business-card
```

## Key Design Decisions
- **FastAPI** for async-native REST API with automatic OpenAPI/Swagger/ReDoc
- **Pydantic v2** for strict request/response validation
- **Environment-based config** via `APIConfig` + environment variables
- **Structured logging** with `request_id` context propagation
- **Lifespan events** (not deprecated `on_event`)
- **AI endpoints return HTTP 501** — no fake predictions
- **5 middleware layers**: CORS, GZip, RequestID, ExecutionTime, Logging
- **Global exception handler** converts all exceptions to `ErrorResponse` JSON

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Environment (development/testing/production) |
| `API_HOST` | `0.0.0.0` | Bind address |
| `API_PORT` | `8000` | Port number |
| `API_RELOAD` | `true` | Auto-reload on code changes |
| `API_LOG_LEVEL` | `INFO` | Logging level |
| `API_CORS_ORIGINS` | `*` | CORS allowed origins |
| `API_SECRET_KEY` | `dev-secret-key` | Secret key for auth |

## Running

```bash
python -m src.api.server
# or via uvicorn:
uvicorn src.api.app:create_app --factory --reload
```

## Tests

- **84 tests** covering all modules (unit: 64, integration: 14, benchmark: 2, stress: 4)
- Run: `pytest tests/unit/api/ tests/integration/api/ tests/benchmark/api/ tests/stress/api/`
- Full suite (all sprints): **219 tests, 100% pass**

## Dependencies
- `fastapi==0.139.0`
- `pydantic==2.13.4`
- `uvicorn==0.51.0`
- No AI, YOLO, or OCR dependencies
