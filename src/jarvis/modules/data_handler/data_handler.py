from importlib import resources
import json

def load_json(path, name):
    with resources.open_text(path, name) as file:
            return json.load(file)