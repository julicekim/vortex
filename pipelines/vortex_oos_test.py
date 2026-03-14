import os
import polars as pl
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix
from brain.core.config import settings
from loguru import logger

def run_oos_test():
    """
    [Vortex 1.0] OOS (Out-of-Sample) 검증 프로세스
    - 훈련에 단 1건도 사용되지 않은 2024~2025 데이터를 봉인 해제하여 모델의 진짜 실력을 검증한다.
    - 이오츠(Iotzu) 샌님의 격리 철학이 빛을 발하는 순간!!
    """
    logger.info(">>> [Phase 3] Vortex 1.0 OOS 검증 프로세스 가동!! (2024-2025)")
    
    # 1. 봉인된 2024~2025 데이터 로드 (sophia_train_v1 하위 oos_test_2024_2025 폴더)
    # 분봉(1Min) 데이터를 우선 검증 대상으로 한다.
    oos_dir = os.path.join(settings.ML_FEATURES_DIR, "sophia_train_v1/oos_test_2024_2025")
    
    if not os.path.exists(oos_dir):
        logger.error(f"OOS 데이터 폴더가 없습니다: {oos_dir}")
        return

    parquet_files = [os.path.join(oos_dir, f) for f in os.listdir(oos_dir) if f.endswith('.parquet')]
    
    if not parquet_files:
        logger.error("병합할 OOS Parquet 파일이 없습니다!!")
        return

    logger.info(f"🔒 봉인 해제: {len(parquet_files)}개의 OOS 데이터를 병합 중... (2024-2025)")
    
    # Polars의 광속 병합 가동!!
    df_list = []
    for f in parquet_files:
        df_list.append(pl.read_parquet(f))
    
    df_oos = pl.concat(df_list)
    logger.info(f"총 {len(df_oos)}행의 미지(Unknown) 데이터셋 로드 완료!!")

    # 2. 피처(X)와 정답지(Y) 분리
    # [Anvil 엔진 규격 반영] 명세서의 명칭과 앤빌의 피처 접두어(feat_)를 맞춘다.
    feature_cols = [
        "feat_vol_surge_ratio", 
        "feat_vwap_dist_pct", 
        "feat_mins_from_open", 
        "feat_atr_compression_ratio"
    ]
    target_col = "target_label"

    X_oos = df_oos.select(feature_cols).to_pandas()
    y_oos = df_oos.select(target_col).to_pandas().values.ravel()
    
    # 3. 소피아의 뇌(모델) 로드
    # [v2.1 업데이트] 균형 잡힌 모델을 우선 로드하여 테스트한다.
    model_name = "vortex_model_v1_balanced.json"
    model_path = os.path.join(settings.MODEL_DIR, model_name)
    if not os.path.exists(model_path):
        # 균형 모델이 없으면 기본 모델 시도
        model_name = "vortex_model_v1.json"
        model_path = os.path.join(settings.MODEL_DIR, model_name)
        
    if not os.path.exists(model_path):
        logger.error(f"모델 파일이 존재하지 않습니다: {model_path}")
        return

    logger.info(f"🧠 Vortex 모델 로드 중... ({model_name})")
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    
    # 4. 미래 데이터 예측 및 채점
    logger.info("🔥 OOS 데이터에 대한 예측 및 성능 평가 시작!!")
    y_pred = model.predict(X_oos)
    
    print("\n🔥 [VORTEX 1.0 - OOS(2024~2025) 최종 성적표] 🔥")
    print("======================================================")
    print("1. 혼돈 행렬 (Confusion Matrix):")
    # [ [진짜 안전(0)을 안전이라 함,  진짜 안전(0)을 위험이라 막음]
    #   [진짜 위험(1)을 안전이라 함,  진짜 위험(1)을 위험이라 막음] ]
    conf_matrix = confusion_matrix(y_oos, y_pred)
    print(conf_matrix)
    
    print("\n2. 상세 지표 (Classification Report):")
    class_report = classification_report(y_oos, y_pred)
    print(class_report)
    print("======================================================")
    
    logger.success("✅ Vortex 1.0 OOS 검증 완료!!")
    logger.info("주니(Junie)야, 이 성적표가 소피아 누님의 실전 방어력이다!! 캬하하!!")

if __name__ == "__main__":
    run_oos_test()
