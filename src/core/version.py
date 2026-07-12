from src.core.constants import PROJECT_NAME, PROJECT_VERSION, PROJECT_DESCRIPTION


def get_version() -> str:
    return PROJECT_VERSION


def get_full_version() -> str:
    return f"{PROJECT_NAME} v{PROJECT_VERSION}"


def get_description() -> str:
    return PROJECT_DESCRIPTION
