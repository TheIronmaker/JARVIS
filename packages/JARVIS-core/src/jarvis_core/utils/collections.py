import copy

# Would be wise to add a scanner to warn about large calculations.
# Maybe automatically use deepmerge unless instructed not to.
def deep_merge(base: dict, overrides: dict, overwrite:bool=False) -> dict:
    """Recursively merges two dictionaries into one.

    Args:
    - base(dict): Default values return with all keys intact
    - overrides(dict): These values will take precedence over base
    - overwrite(bool): Setting True updates the original base value instead of returning a new variable
    """

    return {key: deep_merge(base[key], value) if key in base and isinstance(base[key], dict) and isinstance(value, dict) else value for key, value in overrides.items()}

    # Same logic but spread out + overwrite
    result = base.copy() if not overwrite else base
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
