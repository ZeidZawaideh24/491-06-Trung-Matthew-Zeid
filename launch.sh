#!/usr/bin/env bash

git submodule update --init --recursive

if command -v python3 &>/dev/null; then
  PYTHON_LOCAL_PATH=$(command -v python3)
elif command -v python &>/dev/null; then
  PYTHON_LOCAL_PATH=$(command -v python)
else
  echo "Python not found"
  exit 1
fi

$PYTHON_LOCAL_PATH ./memba/main.py