#!/bin/bash -e

case "$1" in
    "bash")
        exec bash
        ;;
    "web")
        exec uvicorn excars.main:app --host 0.0.0.0 --port ${PORT:-8000}
        ;;
    *)
        exec ${@}
        ;;
esac
