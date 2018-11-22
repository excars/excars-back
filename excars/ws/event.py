import importlib
import pathlib
import pkgutil

_listeners_registry = {}  # pylint: disable=invalid-name
_publishers_registry = []  # pylint: disable=invalid-name
_stream_messages_registry = {}  # pylint: disable=invalid-name


def listen(event_type: str):

    def deco(func):
        _listeners_registry[event_type] = func
        return func

    return deco


def publisher(func):
    _publishers_registry.append(func)
    return func


def stream_handler(message_type: str):
    def deco(func):
        _stream_messages_registry[message_type] = func
        return func

    return deco


def get_listener(event_type: str):
    return _listeners_registry[event_type]


def get_publishers():
    return _publishers_registry.copy()


def get_stream_message_handler(message_type: str):
    return _stream_messages_registry.get(message_type)


def discover():
    pkgs = [
        'excars.ws.listeners',
        'excars.ws.publishers',
        'excars.ws.stream_events',
    ]

    for pkg in pkgs:
        pkg_dir = pathlib.Path(importlib.import_module(pkg).__file__).absolute().parent
        modules = [name for _, name, is_pkg in pkgutil.iter_modules([pkg_dir]) if not is_pkg]

        for module in modules:
            importlib.import_module(f'{pkg}.{module}')
