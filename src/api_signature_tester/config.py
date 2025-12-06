import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


@lru_cache
def load_config() -> dict:
    """
    Carga automática según el ambiente:
    - Variable de entorno APP_ENV: test / dev / prod
    - Default = dev
    """

    env = os.getenv("APP_ENV", "dev").lower()

    # Archivos
    print(CONFIG_DIR)
    base_config = _load_json(CONFIG_DIR / "base.json")
    env_config = _load_json(CONFIG_DIR / f"{env}.json")

    # Mezcla base + archivo del ambiente
    merged = {**base_config, **env_config}

    return merged


class Settings:
    """Acceso a la config desde toda la app."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        raw = load_config()

        self._environment = raw.get("environment")
        self._log_level = raw.get("log_level", "INFO")
        self._initialized = True

    def get_properties(self, key: str) -> Any | None:
        """Return a property value from the loaded config.

        Config values can be any JSON type (string, dict, list, number...), so we
        return Any or None if the key is not present.
        """
        return load_config().get(key, None)

    def get_environment(self) -> str:
        return self._environment

    def get_log_level(self) -> str:
        return self._log_level
