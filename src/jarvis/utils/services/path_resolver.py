# jarvis/utils/services/path_resolver.py
import json
from pathlib import Path
from platformdirs import user_config_dir, user_data_dir, user_cache_dir

"""
Plan (config):
Check if a config file exists in the correct place in platformdirs.user_config_dir
If not, use importlib.resources to read the config file from jarvis and copy it to the user's config directory.
It should load the file from the user's directory from then on.
"""

class FileLoader:
    @staticmethod
    def load_json(path: str):
        with open(path) as f:
            return json.load(f)
    
    @staticmethod
    def load_txt(path: str):
        with open(path) as f:
            return f.read()

class PathResolver:
    """
    A utility class for resolving file paths based on a defined schema.
    
    Capabilities:
    - Resolving paths based on a root schema that defines base directories for different domains (e.g., project, config, cache, data).
    - Attaching and separating file extensions.
    - Loading files based on their resolved paths and formats using a format schema that maps file extensions to loader functions.
    - Handling errors for invalid domains, unsupported file formats, and missing files.
    """

    SCHEMA_ROOT = {
        "PACKAGE": Path(__file__).parent.parent.parent,
        "PROJECT": Path(__file__).parent.parent.parent.parent.parent,
        "CONFIG": Path(user_config_dir("jarvis")),
        "DATA": Path(user_data_dir("jarvis")),
        "CACHE": Path(user_cache_dir("jarvis"))
    }
    SCHEMA_FORMAT = {
        ".json": FileLoader.load_json,
        ".txt": FileLoader.load_txt
    }

    @staticmethod
    def attach_ext(filename: str, extension: str=None) -> str:
        """ Attaches the extension to the filename if it's not already present.
        Args:
            filename (str): The name of the file (with or without extension).
            extension (str, optional): The file extension (e.g., ".json", ".txt).
        Returns:
            str: The filename with the extension attached if it was not already present.
        """
        return filename if not extension or filename.endswith(extension) else filename + PathResolver.format_ext(extension)

    @staticmethod
    def separate_ext(filename: str|Path) -> tuple[str, str]:
        path = Path(filename)
        return path.stem, path.suffix

    @staticmethod
    def format_ext(extension: str) -> str:
        """Ensures the extension starts with a dot."""
        return extension if extension.startswith(".") else f".{extension}"

    @staticmethod
    def resolve_path(filename: str, extension: str=None, domain: str="package", location: str|Path=None) -> Path:
        """ Resolves a file path based on the given parameters and the defined schema.
        Args:
            filename (str): The name of the file (with or without extension).
            extension (str, optional): The file extension (e.g., ".json", ".txt").
            domain (str, optional): The domain/category of the file e.g., "package" (default), "config", "cache", "data"
            location (str | Path, optional): A specific location to look in before checking the schema.
        Returns:
            path (Path): The resolved file path.
        Raises:
            ValueError: If the domain is not valid.
            FileNotFoundError: If the file is not found in the resolved path.
        """

        # Finds Path class directory based on domain
        path = PathResolver.SCHEMA_ROOT.get(domain.upper())
        if not path:
            raise ValueError(f"Invalid domain '{domain}'. Valid domains are: {', '.join(PathResolver.SCHEMA_ROOT.keys())}")
        
        if location:
            path /= location

        path /= PathResolver.attach_ext(filename, extension)
        if path.exists():
            return path
        
        raise FileNotFoundError(path)

    @staticmethod
    def load_file(filename: str, extension: str=None, domain: str="package", location: str|Path=None, *args, **kwargs) -> any:
        """ Loads a file based on the resolved path and returns its contents.
        Args:
            filename (str): The name of the file (extension may be provided in the extension field).
            extension (str, optional): The file extension/type.
            domain (str, optional): The domain/category of the file e.g., "package" (default), "config", "cache", "data"
            location (str | Path, optional): A specific location to look in before checking the schema.
        Returns:
            content: The contents of the loaded file.
        Raises:
            ValueError: If the domain is not valid or if the filename does not match the specified type.
            FileNotFoundError: If the file is not found in the resolved path.
        """
        
        path = PathResolver.resolve_path(filename, extension, domain, location)
        ext = PathResolver.format_ext(extension) if extension else PathResolver.separate_ext(filename)[1]
        loader = PathResolver.SCHEMA_FORMAT.get(ext)
        if not loader:
            raise ValueError(f"Unsupported file format '{ext}'. Currently only {', '.join(PathResolver.SCHEMA_FORMAT.keys())} are supported.")
         
        return loader(path, *args, **kwargs)
