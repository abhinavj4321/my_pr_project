#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input --clear

# Apply database migrations
python manage.py migrate

# Set up production database with default data
echo "👤 Setting up default admin user and data..."
python setup_production_db.py

echo "✅ Build completed successfully!"
