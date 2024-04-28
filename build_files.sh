#!/bin/bash

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Apply database migrations (if necessary)
# /path/to/python3.11 manage.py migrate

# Collect static files
python3.9 manage.py collectstatic --noinput
