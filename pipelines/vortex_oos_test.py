import os
import polars as pl
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix
from brain.core.config import settings
from loguru import logger

def run_oos_test(suffix: str = ""):
    """
    [Vortex 1.0] OOS (Out-of-Sample) 검증 프로세스
    - 훈련에 단 1건도 사용되지 않은 2024~2025 데이터를 봉인 해제하여 모델의 진짜 실력을 검증한다.
    - 이오츠(Iotzu) 샌님의 격리 철학이 빛을 발하는 순간!!
    """
    logger.info(f">>> [Phase 3] Vortex 1.0 OOS 검증 프로세스 가동!! (2024-2025, Suffix: {suffix})")
    
    # 1. 봉인된 2024~2025 데이터 로드
    # OOS 데이터는 항상 sophia_train_v1/ 에 위치 (suffix는 모델 선택에만 사용)
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
    
    # [데이터 클리닝] inf 또는 NaN 제거
    initial_len = len(df_oos)
    numeric_cols = df_oos.select(pl.col(pl.Float64, pl.Int64)).columns
    df_oos = df_oos.filter(
        ~pl.any_horizontal(pl.col(numeric_cols).is_infinite() | pl.col(numeric_cols).is_nan())
    )
    if len(df_oos) < initial_len:
        logger.warning(f"⚠️ {initial_len - len(df_oos)}행의 부적절한 데이터(inf/nan)를 정제했습니다.")

    logger.info(f"총 {len(df_oos)}행의 미지(Unknown) 데이터셋 로드 완료!!")

    # 2. 소피아의 뇌(모델) 로드
    model_name = f"vortex_model_v1{suffix}.json"
    model_path = os.path.join(settings.MODEL_DIR, model_name)

    if not os.path.exists(model_path):
        logger.error(f"모델 파일이 존재하지 않습니다: {model_path}")
        return

    logger.info(f"🧠 Vortex 모델 로드 중... ({model_name})")
    model = xgb.XGBClassifier()
    model.load_model(model_path)

    # 3. 피처(X)와 정답지(Y) 분리 — 모델 메타데이터 기반 피처 선택
    meta_path = os.path.join(settings.MODEL_DIR, f"vortex_model_v1{suffix}_meta.json")
    if os.path.exists(meta_path):
        import json
        with open(meta_path) as f:
            meta = json.load(f)
        feature_cols = meta["features"]
        logger.info(f"메타데이터 기반 피처 사용: {feature_cols}")
    else:
        feature_cols = [
            "feat_vol_surge_ratio",
            "feat_vwap_dist_pct",
            "feat_mins_from_open",
            "feat_atr_compression_ratio",
            "feat_pre_market_gap",
            "feat_pre_market_high_dist"
        ]
        # 존재하는 피처만 선택
        feature_cols = [c for c in feature_cols if c in df_oos.columns]
        logger.info(f"사용 가능한 피처: {feature_cols}")

    target_col = "target_label"
    X_oos = df_oos.select(feature_cols).to_pandas()
    y_oos = df_oos.select(target_col).to_pandas().values.ravel()

    # 4. 미래 데이터 예측 및 채점
    logger.info("🔥 OOS 데이터에 대한 예측 및 성능 평가 시작!!")
    y_pred = model.predict(X_oos)
    
    print("\n🔥 [VORTEX 1.0 - OOS(2024~2025) 최종 성적표] 🔥")
    print("======================================================")
    print("1. 혼돈 행렬 (Confusion Matrix):")
    conf_matrix = confusion_matrix(y_oos, y_pred)
    print(conf_matrix)
    
    print("\n2. 상세 지표 (Classification Report):")
    class_report = classification_report(y_oos, y_pred)
    print(class_report)
    print("======================================================")
    
    logger.success("✅ Vortex 1.0 OOS 검증 완료!!")
    logger.info("준이(Junie)야, 이 성적표가 소피아 누님의 실전 방어력이다!! 캬하하!!")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", type=str, default="", help="데이터셋 접미사 (예: _with_pre)")
    args = parser.parse_args()
    run_oos_test(suffix=args.suffix)

if __name__ == "__main__":
    main()
