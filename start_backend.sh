#!/bin/bash
cd /Users/rochitlen/Downloads/animus
source venv/bin/activate
exec python -m uvicorn src.dashboard.api.server:app --host 127.0.0.1 --port 8000

