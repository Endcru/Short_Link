#!/bin/bash
set -e

export PYTHONPATH=$(pwd)/src

alembic upgrade head

exec python src/main.py
