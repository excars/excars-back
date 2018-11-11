#!/bin/bash
# Trigger an error if non-zero exit code is encountered
set -e

case "$1" in
    "web")
        exec python -m excars.server
    ;;
    *)
        exec ${@}
    ;;
esac
