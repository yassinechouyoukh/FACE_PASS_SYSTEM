"""
ai/model_registry.py
---------------------
Versioned model registry for FacePass.

Reads ``models/registry.json`` to discover available model versions,
then resolves the correct file path based on settings or an explicit
version argument. This makes it easy to A/B test model versions or
roll back without changing any code.

Registry file format (``models/registry.json``):
::

    {
      "default_version": "v1",
      "models": {
        "yolo_face": {
          "v1": "v1/yolo_face.pt",
          "v2": "v2/yolo_face.pt"
        }
      }
    }
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from configs.settings import settings

logger = logging.getLogger(__name__)

_REGISTRY_FILE = "registry.json"


class ModelRegistry:
    """Resolve versioned model file paths from a JSON registry.

    Args:
        model_dir: Root directory containing ``registry.json`` and
                   version sub-directories. Defaults to ``settings.model_dir``.
    """

    def __init__(self, model_dir: Path | None = None) -> None:
        self._model_dir = Path(model_dir or settings.model_dir)
        self._registry: dict = self._load_registry()

    # ── Public API ───────────────────────────────────────────────────────────

    def get_model_path(
        self,
        model_name: str,
        version: str | None = None,
    ) -> Path:
        """Return the absolute path to a versioned model file.

        Args:
            model_name: Key in the registry (e.g. ``"yolo_face"``).
            version:    Version string (e.g. ``"v2"``). Defaults to the
                        value of ``settings.model_version``.

        Returns:
            Resolved ``Path`` to the model file.

        Raises:
            KeyError:  If *model_name* or *version* is not in registry.
            FileNotFoundError: If the resolved file does not exist.
        """
        version = version or settings.model_version
        models = self._registry.get("models", {})

        if model_name not in models:
            raise KeyError(f"Model '{model_name}' not found in registry")
        if version not in models[model_name]:
            available = list(models[model_name].keys())
            raise KeyError(
                f"Version '{version}' not found for '{model_name}'. "
                f"Available: {available}"
            )

        relative = models[model_name][version]
        full_path = self._model_dir / relative

        if not full_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {full_path}. "
                "Did you place the weights in the correct version directory?"
            )

        logger.info("Resolved model '%s@%s' → %s", model_name, version, full_path)
        return full_path

    @property
    def default_version(self) -> str:
        """The default version declared in the registry."""
        return self._registry.get("default_version", settings.model_version)

    @property
    def available_models(self) -> dict:
        """Return the full models section of the registry."""
        return self._registry.get("models", {})

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_registry(self) -> dict:
        registry_path = self._model_dir / _REGISTRY_FILE
        if not registry_path.exists():
            logger.warning(
                "Registry file not found at '%s'. Using empty registry.", registry_path
            )
            return {}
        with open(registry_path, encoding="utf-8") as f:
            data = json.load(f)
        logger.debug("Loaded model registry from '%s'", registry_path)
        return data


# Module-level singleton — import and use directly
registry = ModelRegistry()
