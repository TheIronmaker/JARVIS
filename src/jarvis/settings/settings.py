# jarvis/settings/settings.py
from pathlib import Path

from jarvis.core.data_services import load_json, merge_dictionary, load_merged

SETTINGS_DIR = Path(__file__).parent

def load_core():
    return load_json("core", SETTINGS_DIR, 3)

def load_module_settings(module_type:str) -> dict:
    base = load_json("modules", SETTINGS_DIR)
    load_merged(f"modules/{module_type}", base, default_level=1)


    module_dir = SETTINGS_DIR / "modules" / module_type
    defaults = load_json("default", base=module_dir)
    modules_json = load_json("modules", base=SETTINGS_DIR)
    overrides = modules_json.get(module_type, {})

    return merge_dictionary(defaults, overrides)