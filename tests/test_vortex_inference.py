import xgboost as xgb
import pandas as pd
import os
from brain.core.config import settings
from loguru import logger

def test_vortex_model_inference():
    """
    [Vortex 1.0] 저장된 모델의 추론(Inference) 기능 검증
    - 가상 데이터를 생성하여 모델이 정상적으로 0 또는 1을 예측하는지 확인한다.
    """
    logger.info(">>> Vortex 1.0 모델 추론 검증 시작!!")
    
    model_path = os.path.join(settings.MODEL_DIR, "vortex_model_v1.json")
    
    if not os.path.exists(model_path):
        model_path = os.path.join(settings.MODEL_DIR, "vortex_model_v1_balanced.json")

    # 1. 모델 로드
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    logger.success(f"모델 로드 완료: {model_path}")

    # 2. 가상 데이터 생성 (피처 4종)
    # feat_vol_surge_ratio, feat_vwap_dist_pct, feat_mins_from_open, feat_atr_compression_ratio
    mock_data = pd.DataFrame([
        [1.0, 0.0, 30, 0.5],   # 케이스 1: 일반적인 상황
        [10.0, 2.5, 120, 0.2], # 케이스 2: 거래량 폭발 및 이격도 높은 상황 (위험 확률 높음)
        [0.5, -1.0, 240, 0.8]  # 케이스 3: 진정된 상황
    ], columns=[
        "feat_vol_surge_ratio", 
        "feat_vwap_dist_pct", 
        "feat_mins_from_open", 
        "feat_atr_compression_ratio"
    ])

    # 3. 예측 수행
    preds = model.predict(mock_data)
    probs = model.predict_proba(mock_data)

    for i, (p, prob) in enumerate(zip(preds, probs)):
        logger.info(f"케이스 {i+1} 결과 -> 예측: {p}, 확률(0: {prob[0]:.4f}, 1: {prob[1]:.4f})")
        # 0 또는 1 중 하나여야 함
        assert p in [0, 1]

    logger.success("✅ Vortex 모델 추론 테스트 통과!! 준이(Junie)에게 넘길 준비 완료!!")

if __name__ == "__main__":
    test_vortex_model_inference()
