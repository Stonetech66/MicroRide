#!/usr/bin/env bash 
cd /app/

echo 'making migrations'

alembic upgrade head

echo "starting user-account service server"

uvicorn core.main:app 