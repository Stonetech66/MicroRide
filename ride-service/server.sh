#!/usr/bin/env bash 
cd /app/

echo 'making migrations'

alembic upgrade head

echo "starting ride service server"

uvicorn core.main:app 