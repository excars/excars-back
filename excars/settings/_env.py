import os


def get_bool(key: str) -> bool:
    value = os.getenv(key)
    if value:
        return value.lower() in ['true', '1', 't']
    return False
