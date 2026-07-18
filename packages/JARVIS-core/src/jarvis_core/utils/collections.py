import copy

# Would be wise to add a scanner to warn about large calculations.
# Maybe automatically use deepmerge unless instructed not to.
def deep_merge(base: dict, overrides: dict, overwrite:bool=False) -> dict:
    """Recursively merges two dictionaries into a new one."""
    result = copy.deepcopy(base) if overwrite else base
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result