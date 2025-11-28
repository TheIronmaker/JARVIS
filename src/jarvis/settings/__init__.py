import json
from pathlib import Path

settings_path = Path(__file__).parent / "settings.json"

try:
    with open(settings_path, "r") as f:
        settings = json.load(f)
except Exception as e:
    settings = {}
    from jarvis.app_core import logger
    logger.error(f"Could not load settings.json: {e}")
