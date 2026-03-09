#!/bin/bash

export PYTHONPATH=$(pwd)/src

alembic upgrade head

python src/main.py
