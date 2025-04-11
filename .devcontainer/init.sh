#!/bin/bash
# docker volume rm -f $(basename $PWD)_postgresDB_data || true

set -e
VOLUME_NAME="$(basename $PWD)_postgresDB_data"
echo "Removing Docker volume: $VOLUME_NAME"
docker volume rm -f "$VOLUME_NAME" || true