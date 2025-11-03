#!/usr/bin/env zsh
set -e  # stop if anything fails

# Load environment variables (if .env exists)
if [[ -f .env ]]; then
  echo "Loading environment variables from .env..."
  source .env
else
  echo "⚠️  No .env file found — skipping."
fi

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install --upgrade "openai>=1.60.0" 
pip install tomli-w python-dateutil python-dotenv

echo "✅ Environment initialized and dependencies installed."
echo "👉 You are now inside the virtual environment (.venv)."

