from . import event


def init(request, ws, user):
    return [publisher(request, ws, user) for publisher in event.get_publishers()]
