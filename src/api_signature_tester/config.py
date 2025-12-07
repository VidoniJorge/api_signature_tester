import json
import logging
import os
from functools import lru_cache
from logging import Logger
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"

LOG_LEVEL = "log_level"
CSV_PATH = "csv_path"
REPORT_MD_PATH = "report_md_path"
REPORT_HTML_PATH = "report_html_path"
ENVIRONMENT = "environment"
API_CONFIG_CONTENT_TYPE = "api_config_content_type"


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


@lru_cache
def get_logger() -> Logger:
    class ColorFormatter(logging.Formatter):
        COLORS = {
            logging.DEBUG: "\033[37m",  # Gris
            logging.INFO: "\033[36m",  # Cyan
            logging.WARNING: "\033[33m",  # Amarillo
            logging.ERROR: "\033[31m",  # Rojo
            logging.CRITICAL: "\033[41m",  # Rojo fondo
        }

        RESET = "\033[0m"

        def format(self, record):
            color = self.COLORS.get(record.levelno, self.RESET)
            message = super().format(record)
            return f"{color}{message}{self.RESET}"

    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter("%(asctime)s [%(levelname)s] %(message)s"))

    logger = logging.getLogger("api_signature_tester")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger
