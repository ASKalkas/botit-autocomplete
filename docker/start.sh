#!/usr/bin/env bash
cd /app

# Define cleanup function
cleanup() {
    echo "Running cleanup..."
    rm -rf /app/data/data.json /app/data/unique.txt
    dvc add /app/data
    dvc push
}

# Trap SIGTERM and SIGINT and call cleanup
trap cleanup SIGTERM SIGINT

dvc pull

papermill /app/data.ipynb /dev/null

python /app/autocomplete.py

tail -f /dev/null