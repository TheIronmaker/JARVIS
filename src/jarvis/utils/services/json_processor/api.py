# json_processor.py

import json
from pathlib import Path

from jarvis.core.logger import Logger

def load_json(name: str, base: Path = None, level: int = None) -> dict:
    base = base or Path(__file__).parent
    path = base

    if level:
        for _ in range(level):
            base = base.parent
    
    path = path / f"{name}.json"

    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        Logger.warning(f"No JSON file found: {path}")
        return {}
    except json.JSONDecodeError as e:
        Logger.error(f"Invalid JSON in {path}: {e}")
        return {}
    except Exception as e:
        Logger.error(f"JSON could not load {path}")
        return {}

def load_merged(default: dict | tuple | list, override: dict | tuple | list,) -> dict:
    default_dict = default if isinstance(default, dict) else load_json(*default)
    override_dict = override if isinstance(override, dict) else load_json(*override)
    return merge_dictionary(default_dict, override_dict)

def merge_dictionary(defaults: dict | None, overrides: dict | None) -> dict:
    defaults = defaults or {}
    overrides = overrides or {}
    merged = defaults.copy()
    for k, v in overrides.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = merge_dictionary(merged[k], v)
        else:
            merged[k] = v
    return merged
