# pylint: disable=redefined-outer-name

import argparse

from excars import app


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("port", nargs="?", type=int, default=app.application.config.APP_PORT, help="port to run app")

    return parser


if __name__ == "__main__":
    parser = get_parser()  # pylint: disable=invalid-name
    args = parser.parse_args()  # pylint: disable=invalid-name

    app.application.run(
        host=app.application.config.APP_HOST,
        port=args.port,
        workers=app.application.config.APP_WORKERS,
        debug=app.application.config.APP_DEBUG,
    )
