import os
from typing import List


def get_bool(key: str) -> bool:
    value = os.getenv(key)
    if value:
        return value.lower() in ['true', '1', 't']
    return False


def get_list(key: str, default: List[str] = None) -> List[str]:
    value = os.getenv(key)
    if value:
        return [item.strip() for item in value.split(',')]
    return default or []
