from . import event, views

event.discover()


def init(app):
    app.blueprint(views.bp)
