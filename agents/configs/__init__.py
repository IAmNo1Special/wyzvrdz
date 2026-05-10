"""Structured configuration loader for Wyzvrdz.

This module replaces legacy static constants with dynamic, nested config
objects that directly mirror the project's YAML settings files.
"""

import os
from os import getenv
from pathlib import Path
from types import SimpleNamespace

import yaml

ROOT_DIR = Path(__file__).parent.parent.parent.absolute()


def _load_config(path: Path) -> SimpleNamespace:
    """Helper to load a YAML file and return it as a structured namespace."""

    def _dict_to_namespace(d):
        """Recursively convert dict to SimpleNamespace for dotted access."""
        if isinstance(d, dict):
            return SimpleNamespace(
                **{k: _dict_to_namespace(v) for k, v in d.items()}
            )
        return d

    if not path.exists():
        print(f"Warning: Configuration file not found at {path}")
        return SimpleNamespace()
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return _dict_to_namespace(data)
    except Exception as e:
        print(f"Error parsing configuration at {path}: {e}")
        return SimpleNamespace()


WYZVRD_CONFIGS_DIR = Path(__file__).parent
WYZVRD_SETTINGS = _load_config(WYZVRD_CONFIGS_DIR / "wyzvrd_settings.yaml")

# Support OneDrive Desktop paths by allowing full path override via env var
RAW_WISDOM_PATH = Path(
    getenv(
        "RAW_WISDOM_PATH",
        Path.home() / "Desktop" / getenv("RAW_WISDOM_DIR", "raw_wisdom"),
    )
)

# Filesystem skill base directory - all file operations constrained to this path
# Ensures filesystem scripts only operate within skill's assets directory
FILESYSTEM_ASSETS_PATH = Path(
    os.environ.get("FILESYSTEM_ASSETS_DIR")
    or (Path(__file__).parent.parent / "skills" / "filesystem" / "assets")
)

# Compendium assets directory - the knowledge base storage location
# Used by compendium skill scripts to ensure they write to the correct location
# even when executed via ADK's temp directory materialization
COMPENDIUM_ASSETS_PATH = Path(
    os.environ.get("COMPENDIUM_DIR")
    or (
        Path(__file__).parent.parent
        / "sub_agents"
        / "compendium_mgmt_agent"
        / "skills"
        / "compendium"
        / "assets"
        / "compendium"
    )
)

# Cron-manager assets directory - stores cron job registry
# Must persist beyond ADK temp directory execution
CRON_MANAGER_ASSETS_PATH = Path(
    os.environ.get("CRON_MANAGER_ASSETS_DIR")
    or (Path(__file__).parent.parent / "skills" / "cron-manager" / "assets")
)

# Location skill assets directory - stores location override
# Must persist beyond ADK temp directory execution
LOCATION_ASSETS_PATH = Path(
    os.environ.get("LOCATION_ASSETS_DIR")
    or (Path(__file__).parent.parent / "skills" / "location" / "assets")
)

__all__ = [
    "WYZVRD_SETTINGS",
    "RAW_WISDOM_PATH",
    "WYZVRD_CONFIGS_DIR",
    "FILESYSTEM_ASSETS_PATH",
    "COMPENDIUM_ASSETS_PATH",
    "CRON_MANAGER_ASSETS_PATH",
    "LOCATION_ASSETS_PATH",
    "ROOT_DIR",
]
