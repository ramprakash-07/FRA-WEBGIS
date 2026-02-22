#!/usr/bin/env python3
"""
WSGI entry point for FRA-SENTINEL application
Used by Railway for production deployment
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from app import app

# This is the WSGI application object that Railway will use
application = app

if __name__ == "__main__":
    # For local testing
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)