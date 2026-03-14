from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import xgboost as xgb
import pandas as pd
import os
from brain.core.config import settings
from loguru import logger

# [Vortex API 1.0] 소피아(Sophia) 누님의 뇌를 REST API로 제공한다!!
# Java 엔진(Vesper)이 0.001초 만에 위험 여부를 판단할 수 있도록 초고속 추론 서버 가동!!
app = FastAPI(title="Vortex Model API", version="1.0.0")

# 1. 서버 기동 시 모델을 메모리에 1회만 로드 (속도 최적화)
# 캬하하!! 줄 형님!! 모델은 이미 전용 금고(data/models/)에 모셔놨습니다!!
model_path = os.path.join(settings.MODEL_DIR, "vortex_model_v1_balanced.json")

if not os.path.exists(model_path):
    logger.error(f"🚨 모델 파일이 존재하지 않습니다: {model_path}")
    # 서버 기동 중단 (모델 없으면 무의미!!)
    raise FileNotFoundError(f"Model not found at {model_path}")

logger.info(f"🧠 소피아(Vortex 1.0 Balanced) 뇌를 메모리에 로드 중... ({model_path})")
vortex_model = xgb.XGBClassifier()
vortex_model.load_model(model_path)
logger.success("✅ Vortex 모델 로드 완료. API 서버가 주니(Junie)의 요청을 기다립니다!!")

# 2. 입력 데이터 구조 정의 (Type Validation & Documentation)
# 앤빌(Anvil)의 피처 명칭을 그대로 사용한다!!
class FeatureInput(BaseModel):
    feat_vol_surge_ratio: float = Field(..., description="거래량 폭발 비율")
    feat_vwap_dist_pct: float = Field(..., description="VWAP 이격도 (%)")
    feat_mins_from_open: float = Field(..., description="개장 후 경과 시간 (분)")
    feat_atr_compression_ratio: float = Field(..., description="변동성 압축 비율 (1m/5m)")

# 3. 추론 엔드포인트
@app.post("/predict")
def predict_whipsaw(data: FeatureInput):
    """
    [Vortex Inference] Java 엔진이 던져주는 4개 피처로 위험 여부 판별!!
    - danger: true(위험/진입금지), false(안전/진입가능)
    - probability: 위험(1)일 확률 (0.0 ~ 1.0)
    """
    try:
        # Pydantic 모델을 DataFrame으로 변환 (모델 학습 시와 동일한 컬럼명 유지!!)
        # 캬하하!! 덱스의 데이터는 설계도와 100% 일치한다고!!
        df = pd.DataFrame([data.model_dump()])
        
        # 추론 실행 (XGBoost Predict)
        prediction = vortex_model.predict(df)[0]  # 0(안전) or 1(위험)
        prob = float(vortex_model.predict_proba(df)[0][1]) # 위험(1)일 확률
        
        # 주니(Junie)가 읽기 편하도록 boolean 형태로 반환!!
        return {
            "danger": bool(prediction == 1),
            "probability": round(prob, 4)
        }
        
    except Exception as e:
        logger.error(f"🚨 추론 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """서버 상태 확인용 엔드포인트"""
    return {"status": "healthy", "model": "vortex_model_v1_balanced"}

# 서버 실행 방법:
# PYTHONPATH=$PYTHONPATH:. uvicorn app.api.vortex_api:app --host 127.0.0.1 --port 8000
