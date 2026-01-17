from pathlib import Path

from jarvis.core.logger import Logger
from jarvis.utils.data_services import load_json, merge_dictionary

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
    
    def construct(self, struct: dict, package:list=[], start_struct:bool=True):
        package = package.copy()
        if not struct.get("enabled", True):
            return None

        struct_type = struct.get("type")
        if not struct_type:
            return "Struct type not provided"
        if struct_type not in self.classes:
            return f"Class does not exist for struct type: {struct_type}"
        if struct_type not in self.defaults:
            self.defaults[struct_type] = load_json(self.default_dir[1], self.default_dir[0] / struct_type)
        
        struct_name = struct.get("name") or struct_type
        if struct_name in self.nodes:
            return f"Struct already exists in main struct: {struct_name}"

        # Create class arguments
        if start_struct:
            self.start_node(struct_type, struct_name, package, struct.get("settings", {}))
        
    def start_node(self, struct_type, struct_name, package, settings:dict={}):
        if settings is not False:
            package.append(merge_dictionary(self.defaults.get(struct_type), settings))

        try:
            instance = self.classes[struct_type](struct_name, *package)
            self.nodes[struct_name] = instance
        except Exception as e:
            Logger.error(f"Initialization failed for {struct_name}: {e}")
            return False
        return True