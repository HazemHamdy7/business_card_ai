from __future__ import annotations

VERSION = "0.1.0"
TITLE = "Business Card AI API"
DESCRIPTION = "Production-ready REST API for Business Card AI project"
API_VERSION = "v1"


def get_version_info() -> dict:
    return {
        "version": VERSION,
        "api_version": API_VERSION,
        "title": TITLE,
        "description": DESCRIPTION,
    }
