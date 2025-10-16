#!/bin/bash

# Exit immediately on error
set -e

# Start Redis (if not already running)
echo "🔄 Starting Redis..."
sudo systemctl start redis

# Path to your venv
VENV_DIR="./.venv"

# Activate the venv
if [ -d "$VENV_DIR" ]; then
  echo "🐍 Activating virtual environment..."
  source "$VENV_DIR/bin/activate"
else
  echo "❌ Virtual environment not found at $VENV_DIR"
  exit 1
fi

# Run the worker
echo "🚀 Running worker..."
python -m workers.worker


### 🔧 Run the worker

To start the Redis worker locally:

```bash
./run_worker.sh
Make sure you have a virtual environment set up in .venv/:

bash
Copy code
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt