#!/bin/sh
# Script called from parent directory
gunicorn flask_app:app --worker-class gevent -b 0.0.0.0:$PORT 