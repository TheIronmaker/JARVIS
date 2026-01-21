from pathlib import Path

from jarvis.core.logger import Logger
from jarvis.utils.services.json_processor import load_json, merge_dictionary

class Manager:    
    def initialize(self, classes, main_dir:tuple[Path, str], default_dir:tuple[Path, str]):
        self.classes = classes
        self.default_dir = default_dir
        self.build = load_json(main_dir[1], main_dir[0])
        self.defaults = {}
        self.nodes = {}

    def load_structs(self, package:dict=[], start_structs:bool=True):
        for struct in self.build.get("instances", []):
            msg = self.construct(struct, package, start_structs)
            if isinstance(msg, str):
                Logger.error(f"Struct failed to build. {msg}")
    
    def construct(self, struct: dict, package: any=[], start_struct:bool=True) -> any:
        package = list(package).copy()
        if not struct.get("enabled", True):
            return None

        settings = struct.get("settings", False)

        struct_type = struct.get("type")
        if not struct_type:
            return "Struct type not provided"
        if struct_type not in self.classes:
            return f"Class does not exist for struct type: {struct_type}"
        if struct_type not in self.defaults and settings:
            self.defaults[struct_type] = load_json(self.default_dir[1], self.default_dir[0] / struct_type)
        
        struct_name = struct.get("name") or struct_type
        if struct_name in self.nodes:
            return f"Struct already exists in main struct: {struct_name}"

        # Create class arguments
        if start_struct:
            return self.start_node(struct_type, struct_name, package, settings)
        
    def start_node(self, struct_type, struct_name, package, settings:dict=None):
        if settings is not False:
            package.append(merge_dictionary(self.defaults.get(struct_type), settings))

        try:
            instance = self.classes[struct_type](struct_name, *package)
            self.nodes[struct_name] = instance
            return instance
        except Exception as e:
            return f"Initialization failed: {e}"