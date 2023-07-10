#!/usr/bin/env bash 
cd /app/

echo 'making migrations'

alembic upgrade head

echo "starting driver service server"

uvicorn core.main:app 