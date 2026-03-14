#!/bin/bash
# Vortex 모델 학습 실행 스크립트!!
export PYTHONPATH=$PYTHONPATH:$(pwd)
uv run python pipelines/run_train.py "$@"
