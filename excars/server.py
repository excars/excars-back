from excars import app

if __name__ == '__main__':
    app.application.run(
        host=app.application.config.APP_HOST,
        port=app.application.config.APP_PORT,
        workers=app.application.config.APP_WORKERS,
        debug=app.application.config.APP_DEBUG,
    )
