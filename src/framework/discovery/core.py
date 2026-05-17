import importlib
import inspect
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from framework.apps.config import AppConfig


def _import_app_config(app_path: str) -> "AppConfig | None":
    """Import and instantiate AppConfig subclass from `<app_path>.apps` module."""
    try:
        mod = importlib.import_module(f"{app_path}.apps")
    except Exception:
        return None

    from framework.apps.config import AppConfig

    for _name, obj in inspect.getmembers(mod, inspect.isclass):
        if issubclass(obj, AppConfig) and obj is not AppConfig and obj.__module__ == mod.__name__:
            try:
                return obj()
            except Exception:
                continue

    # fallback: module-level `config` instance
    maybe = getattr(mod, "config", None)
    if maybe is not None:
        from framework.apps.config import AppConfig as _AC

        if isinstance(maybe, _AC):
            return maybe

    return None


def discover_app_paths(package: str = "apps") -> list[str]:
    """Return dotted import paths for all first-level packages under `apps`
    that contain a valid AppConfig subclass in their `apps.py` module.
    """
    try:
        pkg = importlib.import_module(package)
    except Exception:
        return []

    discovered: list[str] = []
    for _finder, name, ispkg in pkgutil.iter_modules(pkg.__path__, prefix=f"{package}."):
        if not ispkg:
            continue
        if _import_app_config(name) is not None:
            discovered.append(name)
    return discovered


def load_app_configs(app_paths: list[str]) -> list["AppConfig"]:
    """Load and filter enabled AppConfig instances from given paths."""
    import logging

    logger = logging.getLogger(__name__)
    configs: list[AppConfig] = []
    disabled: list[str] = []

    for path in app_paths:
        cfg = _import_app_config(path)
        if cfg is None:
            continue
        if cfg.is_enabled():
            configs.append(cfg)
        else:
            disabled.append(f"{cfg.name} ({cfg.label})")

    if configs:
        active = [f"{c.name} ({c.label})" for c in configs]
        logger.info(
            f"Loaded {len(configs)} active app{'s' if len(configs) != 1 else ''}: "
            f"{', '.join(active)}"
        )
    else:
        logger.warning("No active applications found")

    if disabled:
        logger.info(f"Disabled apps: {', '.join(disabled)}")

    return configs
