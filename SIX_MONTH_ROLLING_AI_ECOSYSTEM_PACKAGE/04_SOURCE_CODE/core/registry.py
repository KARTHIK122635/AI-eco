import json
import importlib
import os
from typing import Dict, Type, List, Optional
from sources.base import BaseCollector


class SourceRegistry:
    """
    Configurable Source Registry that allows adding, configuring,
    and managing directories dynamically without modifying the core scraper.
    """
    _registry: Dict[str, Type[BaseCollector]] = {}

    def __init__(self, config_path: str = "config/sources_config.json"):
        self.config_path = config_path
        self.configs: Dict[str, dict] = {}
        self.load_configuration()

    @classmethod
    def register(cls, source_id: str, collector_cls: Type[BaseCollector]):
        """Programmatic registration of a new collector class."""
        cls._registry[source_id] = collector_cls

    def load_configuration(self):
        """Loads declarative configuration and registers collector classes dynamically."""
        if not os.path.exists(self.config_path):
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for src in data.get("sources", []):
            src_id = src["id"]
            self.configs[src_id] = src

            # Dynamically import the class if not already registered
            if src_id not in self._registry and "class" in src:
                module_name, class_name = src["class"].rsplit(".", 1)
                try:
                    mod = importlib.import_module(module_name)
                    cls_obj = getattr(mod, class_name)
                    self._registry[src_id] = cls_obj
                except Exception as e:
                    print(f"Warning: Could not load source '{src_id}': {e}")

    def get_collector(self, source_id: str) -> Optional[BaseCollector]:
        """Instantiates a collector with its registered configuration."""
        if source_id not in self._registry:
            return None
        cfg = self.configs.get(source_id, {})
        cls_obj = self._registry[source_id]
        return cls_obj(config=cfg)

    def list_available_sources(self) -> List[dict]:
        """Returns metadata for all registered sources."""
        sources = []
        for src_id, cls_obj in self._registry.items():
            cfg = self.configs.get(src_id, {})
            sources.append({
                "id": src_id,
                "display_name": getattr(cls_obj, "display_name", src_id),
                "base_url": getattr(cls_obj, "base_url", ""),
                "enabled": cfg.get("enabled", True),
                "description": cfg.get("description", "")
            })
        return sources

    def add_source_config(self, source_id: str, class_path: str, base_url: str,
                          rate_limit: float = 1.0, max_concurrency: int = 2,
                          description: str = "", enabled: bool = True):
        """Allows dynamically adding a new directory configuration and saving it."""
        new_entry = {
            "id": source_id,
            "class": class_path,
            "enabled": enabled,
            "base_url": base_url,
            "rate_limit_delay": rate_limit,
            "max_concurrency": max_concurrency,
            "description": description
        }
        self.configs[source_id] = new_entry
        # Save back to file
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        sources_list = list(self.configs.values())
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump({"sources": sources_list}, f, indent=2)
        # Reload
        self.load_configuration()
