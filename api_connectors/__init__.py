# type: ignore[attr-defined]
"""'api-connectors' is a Python package created to handle API connections."""
from importlib import metadata as importlib_metadata

from api_connectors import APIClient


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()

__all__ = ["APIClient"]
