"""
Environment Variable Loader
Loads .env from project root safely if environment variables are not already present in os.environ.
Never logs or exposes secret values.
"""

import os
from typing import Dict


def load_project_env(env_path: str = None) -> Dict[str, str]:
    """
    Loads key-value pairs from .env into os.environ if not already defined.
    Does not overwrite existing environment variables.
    """
    if env_path is None:
        # Look in workspace root (parent of core directory or current working directory)
        cwd_env = os.path.join(os.getcwd(), ".env")
        core_parent_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        if os.path.exists(cwd_env):
            env_path = cwd_env
        elif os.path.exists(core_parent_env):
            env_path = core_parent_env
        else:
            return {}

    loaded = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    if key and key not in os.environ:
                        os.environ[key] = val
                        loaded[key] = "***"  # masked
        except Exception:
            pass
    return loaded
