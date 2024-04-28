#!/bin/bash

# Navigate to the project directory
cd /path/to/your/project

# Activate the virtual environment (if using one)
source /path/to/your/venv/bin/activate

# Install dependencies from requirements.txt
/path/to/python3.9 -m pip install -r requirements.txt

# Apply database migrations (if necessary)
# /path/to/python3.11 manage.py migrate

# Collect static files
/path/to/python3.9 manage.py collectstatic --noinput
