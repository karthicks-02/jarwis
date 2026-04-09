#!/bin/bash
PYTHON=/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3
echo "Starting Jarwis with $(${PYTHON} --version)..."
PYTHONUNBUFFERED=1 ${PYTHON} -u "$(dirname "$0")/main.py"
