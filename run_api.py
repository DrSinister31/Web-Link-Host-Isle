#!/usr/bin/env python
"""Uvicorn ASGI loader for FastAPI"""
import sys
import os

# Ensure /app is in the path
sys.path.insert(0, '/app')

import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'bridge.synix_api:app',
        host='0.0.0.0',
        port=8000,
        reload=False
    )
