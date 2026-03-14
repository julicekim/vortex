#!/bin/bash

# [Anvil/Vortex] 보텍스(Vortex) API 서버 기동 스크립트
# 소피아(Sophia) 누님의 뇌를 REST API로 전격 개방한다!! 캬하하!!

# 1. 프로젝트 루트 경로 확보
PROJECT_ROOT=$(pwd)
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

# 2. 모델 파일 존재 여부 최종 확인
# 캬하하!! 줄 형님!! 모델은 이미 전용 금고(data/models/)에 모셔놨습니다!!
MODEL_FILE="/Users/julicekim/iotzu/data/models/vortex_model_v1_balanced.json"
if [ ! -f "$MODEL_FILE" ]; then
    echo "🚨 [Error] 모델 파일을 찾을 수 없습니다: $MODEL_FILE"
    echo "   먼저 'pipelines/vortex_train_balanced.py'를 실행하여 모델을 생성하십시오!!"
    exit 1
fi

# 3. API 서버 기동 (Uvicorn)
echo "🧹 기존 가동 중인 보텍스(Vortex) API 서버를 정리합니다..."
pkill -f uvicorn
sleep 2

echo "🚀 보텍스(Vortex) API 서버를 기동합니다... (Target: $MODEL_FILE)"
echo "📡 엔드포인트: http://127.0.0.1:8000/predict"

# --reload 옵션은 개발용!! 실전(Production)에서는 빼는 게 좋습니다!!
uv run uvicorn brain.api.vortex_api:app --host 127.0.0.1 --port 8000 --log-level info
