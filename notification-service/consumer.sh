#!/bin/sh
cd /app/

echo "starting notification service consumer >>>"

python -m core.consumers
 
