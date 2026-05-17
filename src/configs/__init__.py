import os
import warnings

from pydantic import ValidationError
from pydantic_settings import SettingsError

from .settings import Settings

# Suppress missing Docker secrets directories noise in local runs
warnings.filterwarnings("ignore", message='directory "/run/secrets" does not exist')
warnings.filterwarnings("ignore", message='directory "/etc/secrets" does not exist')

RAW_ERRORS = os.getenv("SETTINGS_RAW_ERRORS") == "1"

if RAW_ERRORS:
    settings = Settings()
else:
    try:
        settings = Settings()
    except (SettingsError, ValidationError, ValueError) as exc:
        message = (
            "Configuration error while loading Settings.\n"
            f"Details: {exc}\n\n"
            "Hints:\n"
            '- For list fields (e.g., CORS_ORIGINS) use JSON: CORS_ORIGINS=["http://localhost:3000"]\n'
            "- Check your environment variables and .env for typos or invalid JSON.\n"
        )
        raise RuntimeError(message) from None

__all__ = ["Settings", "settings"]
