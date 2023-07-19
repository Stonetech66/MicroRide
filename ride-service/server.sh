#!/bin/sh

cd /app/

echo 'making migrations'

alembic upgrade head

echo "starting ride service server"

uvicorn core.main:app --host 0.0.0.0