#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def detect_settings_module() -> str:
    """Try to detect the project's settings module from repository layout."""
    default_module = "bd_lab3.settings"
    base_dir = Path(__file__).resolve().parent

    default_path = base_dir / "bd_lab3" / "settings.py"
    if default_path.exists():
        return default_module

    for candidate in base_dir.iterdir():
        if candidate.is_dir() and (candidate / "settings.py").exists():
            return f"{candidate.name}.settings"

    return default_module


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", detect_settings_module())
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your "
            "PYTHONPATH environment variable? Did you forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
