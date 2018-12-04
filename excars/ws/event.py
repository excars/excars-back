import importlib
import pathlib
import pkgutil

_listeners_registry = {}  # pylint: disable=invalid-name
_publishers_registry = []  # pylint: disable=invalid-name
_consumers_registry = {}  # pylint: disable=invalid-name


def listen(event_type: str):

    def deco(func):
        _listeners_registry[event_type] = func
        return func

    return deco


def publisher(func):
    _publishers_registry.append(func)
    return func


def consume(message_type: str):
    def deco(func):
        _consumers_registry[message_type] = func
        return func

    return deco


def get_listener(event_type: str):
    return _listeners_registry[event_type]


def get_publishers():
    return _publishers_registry.copy()


def get_consumers(message_type: str):
    return _consumers_registry.get(message_type)


def discover():
    pkgs = [
        'excars.ws.listeners',
        'excars.ws.publishers',
        'excars.ws.consumers',
    ]

    for pkg in pkgs:
        pkg_dir = pathlib.Path(importlib.import_module(pkg).__file__).absolute().parent
        modules = [name for _, name, is_pkg in pkgutil.iter_modules([pkg_dir]) if not is_pkg]

        for module in modules:
            importlib.import_module(f'{pkg}.{module}')
