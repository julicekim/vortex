from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
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
# 앤빌(Anvil)의 피처 명칭을 그대로 사용하되, 주니(Junie)의 Vesper 요청 편의를 위해 별칭(Alias) 부여!!
# [IMPORTANT] Pydantic V2에서는 alias가 설정되면 요청 시 해당 이름으로 필드를 찾아야 함!!
class FeatureInput(BaseModel):
    # 🚨 Pydantic V2 철벽 방어: 원래 이름과 별칭 모두 허용
    model_config = ConfigDict(populate_by_name=True)

    vol_surge_ratio: float = Field(..., description="거래량 폭발 비율")
    vwap_dist_pct: float = Field(..., description="VWAP 이격도 (%)")
    mins_from_open: float = Field(..., description="개장 후 경과 시간 (분)")
    atr_compression_ratio: float = Field(..., description="변동성 압축 비율 (1m/5m)")

# 3. 추론 엔드포인트
@app.post("/predict")
def predict_whipsaw(data: FeatureInput):
    """
    [Vortex Inference] Java 엔진이 던져주는 4개 피처로 위험 여부 판별!!
    - danger: true(위험/진입금지), false(안전/진입가능)
    - probability: 위험(1)일 확률 (0.0 ~ 1.0)
    """
    try:
        # [CRITICAL FIX] 모델 학습 시 사용된 원본 피처명(feat_...)으로 수동 매핑하여 DataFrame 생성!!
        # Pydantic Alias 이슈를 완전히 우회하여 정합성을 확보한다!!
        input_dict = {
            "feat_vol_surge_ratio": data.vol_surge_ratio,
            "feat_vwap_dist_pct": data.vwap_dist_pct,
            "feat_mins_from_open": data.mins_from_open,
            "feat_atr_compression_ratio": data.atr_compression_ratio
        }
        
        # [Dex's Detailed Logging] 줄(JUL) 형님 요청: 추론 요청 데이터 상세 기록!!
        logger.info(f"📥 [Predict Request] Features: {input_dict}")
        
        df = pd.DataFrame([input_dict])
        
        # 추론 실행 (XGBoost Predict)
        # XGBClassifier는 DataFrame의 컬럼명을 확인하므로, feat_ 접두사가 반드시 있어야 함!!
        prediction = vortex_model.predict(df)[0]  # 0(안전) or 1(위험)
        prob = float(vortex_model.predict_proba(df)[0][1]) # 위험(1)일 확률
        
        # [Dex's Detailed Logging] 추론 결과 상세 기록!!
        result = {
            "danger": bool(prediction == 1),
            "probability": round(prob, 4)
        }
        logger.info(f"📤 [Predict Result] {result}")
        
        # 주니(Junie)가 읽기 편하도록 boolean 형태로 반환!!
        return result
        
    except Exception as e:
        logger.error(f"🚨 추론 중 에러 발생: {e}")
        # 상세 에러 메시지 포함 (디버깅 용)
        raise HTTPException(status_code=500, detail=f"Inference Error: {str(e)}")

@app.get("/health")
def health_check():
    """서버 상태 확인용 엔드포인트"""
    return {"status": "healthy", "model": "vortex_model_v1_balanced"}

# 서버 실행 방법:
# PYTHONPATH=$PYTHONPATH:. uvicorn app.api.vortex_api:app --host 127.0.0.1 --port 8000
