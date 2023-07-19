#!/usr/bin/env bash

cd /app/

echo 'making migrations'

alembic upgrade head

echo "starting tracking service server"

uvicorn core.main:app --host 0.0.0.0