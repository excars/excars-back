from excars.app import app

if __name__ == '__main__':
    app.run(
        host=app.config.APP_HOST,
        port=app.config.APP_PORT,
        workers=app.config.APP_WORKERS,
        debug=app.config.APP_DEBUG,
    )
