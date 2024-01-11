#!/bin/bash

# Move to project directory
# shellcheck disable=SC2164
cd /websocket_example

# Start server through gunicorn
echo "Starting server through uvicorn"
uvicorn ws_fastapi_server.ws_app --reload --host 0.0.0.0 --port 8080