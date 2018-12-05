from . import views


def init(app):
    app.blueprint(views.bp)
