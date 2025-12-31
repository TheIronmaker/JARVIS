# jarvis/settings/settings.py

import json
from pathlib import Path

from jarvis.core.logger import Logger

_dir = Path(__file__).parent

class Settings:
    def load(self, name:str, paths:list = None) -> dict:
        paths = paths or []
        name += ".json"
        entry = _dir
        
        if paths is None:
            entry = entry / name

        for p in paths:
            candidate = _dir.parent / p / name
            if candidate.exists():
                entry = candidate
                return self.load_json(entry)
            
        return self.load_json(entry)

    @staticmethod
    def load_json(entry:Path) -> dict:
        try:
            with open(entry, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            Logger.warning(f"No settings file found: {entry}")
            return {}
        except json.JSONDecodeError as e:
            Logger.error(f"Invalid JSON in {entry}: {e}")
            return {}
        except Exception as e:
            Logger.error(f"Could not load {entry}: {e}")
            return {}
        
    @staticmethod
    def merge_settings(defaults: dict, overrides: dict) -> dict:
        result = defaults.copy()
        result.update(overrides)
        return result