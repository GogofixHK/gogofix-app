#!/bin/bash
PORT=${PORT:-8000}
echo "Starting GoGofix on port $PORT, DATA_DIR=$DATA_DIR"
exec python3 -m uvicorn gogofix_api:app --host 0.0.0.0 --port $PORT --log-level info
