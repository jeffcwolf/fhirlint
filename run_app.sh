#!/bin/bash
# FHIR Quality Inspector Launcher

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run application
python src/main.py
