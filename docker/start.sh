#!/usr/bin/env bash
cd /app

dvc pull

papermill /app/data.ipynb /dev/null

python /app/autocomplete.py

tail -f /dev/null