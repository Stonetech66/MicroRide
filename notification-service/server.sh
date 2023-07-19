#!/bin/sh
cd /app/

echo "starting notification service server"

uvicorn core.main:app --host 0.0.0.0