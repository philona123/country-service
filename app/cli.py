import subprocess
import sys
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def dev() -> None:
    """Run FastAPI dev server with reload."""
    result = subprocess.run(
        ["fastapi", "dev", "app/main.py"],
        cwd=_project_root(),
    )
    raise SystemExit(result.returncode)


def test() -> None:
    """Run unit tests."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit", "-v"],
        cwd=_project_root(),
    )
    raise SystemExit(result.returncode)


def test_integration() -> None:
    """Run integration tests (requires MongoDB; uses country_db_test)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration", "-v"],
        cwd=_project_root(),
    )
    raise SystemExit(result.returncode)


def test_all() -> None:
    """Run unit and integration tests."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-v"],
        cwd=_project_root(),
    )
    raise SystemExit(result.returncode)
