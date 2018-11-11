#!/bin/bash -e

case "$1" in
    "web")
        exec python -m excars.server
    ;;
    *)
        exec ${@}
    ;;
esac
