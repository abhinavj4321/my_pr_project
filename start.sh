#!/usr/bin/env bash
# exit on error
set -o errexit

# Run gunicorn
exec gunicorn student_management_system.wsgi:application