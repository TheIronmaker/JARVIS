
from pathlib import Path

# Supported loaders - should be using importlib throughout project...
import json
import yaml


class FileManager:
    @staticmethod
    def load_json(path: str | Path, config: dict = {}):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @staticmethod
    def load_txt(path: str | Path, config: dict = {}):
        with open(path, "r", encoding=config.get("encoding", "utf-8")) as f:
            return f.read()
    
    @staticmethod
    def load_YAML(path: str | Path, config: dict = {}):
        with open(path, "r", encoding=config.get("encoding", "utf-8")) as f:
            return yaml.safe_load(f)

class ParserYAML:
    def get_defaults(data:dict):
        """Pulls out all attr values for a yaml dictionary"""
        pass
