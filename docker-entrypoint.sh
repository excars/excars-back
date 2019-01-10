#!/bin/bash -e

case "$1" in
    "bash")
        exec bash
        ;;
    "web")
        exec python -m excars.server ${PORT}
        ;;
    *)
        exec ${@}
        ;;
esac
