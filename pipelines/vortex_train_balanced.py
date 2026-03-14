import os
import polars as pl
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix
from brain.core.config import settings
from loguru import logger

def train_vortex_balanced():
    """
    [Vortex 2.1] 덱스(Dex)의 언더샘플링(Under-sampling) 5:5 황금비율 세팅
    - 흔해 빠진 위험(1) 데이터를 귀한 안전(0) 데이터 개수에 맞춰 소각한다!!
    - 소피아(Sophia) 누님의 뇌 영점 조절: 가중치(scale_pos_weight)를 제거하고 진짜 패턴을 보게 한다.
    """
    logger.info(">>> [Phase 2.1] Vortex 언더샘플링 파이프라인 가동!! 캬하하!!")
    
    # 1. 훈련 데이터(2018~2023) 병합
    train_dir = os.path.join(settings.ML_FEATURES_DIR, "sophia_train_v1/train_2018_2023")
    parquet_files = [os.path.join(train_dir, f) for f in os.listdir(train_dir) if f.endswith('.parquet')]
    
    logger.info(f"📦 훈련 데이터 병합 중... ({len(parquet_files)} tickers)")
    df_train = pl.concat([pl.read_parquet(f) for f in parquet_files])
    
    # ---------------------------------------------------------
    # ⚖️ [핵심] 언더샘플링 (Under-sampling) 로직 추가
    # ---------------------------------------------------------
    # 0(안전/수익권), 1(위험/횡보) 분리
    df_safe = df_train.filter(pl.col("target_label") == 0)
    df_danger = df_train.filter(pl.col("target_label") == 1)
    
    min_count = df_safe.height # 안전(0) 데이터의 개수 확보
    logger.info(f"📉 쓰레기 소각 준비: 안전({min_count}개) vs 위험({df_danger.height}개)")
    
    # 위험(1) 데이터를 안전(0) 개수만큼만 랜덤 추출 (seed=42 고정)
    # 캬하하!! 1,200만 개의 위험 데이터를 93만 개로 싹둑 잘라버릴게!!
    df_danger_sampled = df_danger.sample(n=min_count, seed=42)
    
    # 다시 합치고 무작위 셔플(Shuffle) - 소피아 누님이 순서를 외우면 안 되니까!!
    df_balanced = pl.concat([df_safe, df_danger_sampled]).sample(fraction=1.0, seed=42)
    logger.info(f"⚖️ 1:1 황금비율 데이터셋 완성!! 총 {df_balanced.height}행 학습 대기 중.")
    # ---------------------------------------------------------
    
    # 2. 피처(X)와 정답지(Y) 분리
    feature_cols = [
        "feat_vol_surge_ratio", 
        "feat_vwap_dist_pct", 
        "feat_mins_from_open", 
        "feat_atr_compression_ratio"
    ]
    target_col = "target_label"

    X_train = df_balanced.select(feature_cols).to_pandas()
    y_train = df_balanced.select(target_col).to_pandas().values.ravel()
    
    # 3. XGBoost 모델 세팅 (소피아의 영점 조절)
    logger.info("🧠 소피아(Sophia) 누님의 균형 데이터 학습 시작... 가중치 제거 및 깊이 강화!!")
    model = xgb.XGBClassifier(
        max_depth=4,              # 깊이를 4로 살짝 올려서 디테일한 패턴을 보게 함
        learning_rate=0.05,
        n_estimators=150,         # 트리 개수를 150개로 늘려서 지능 지수를 높임
        # scale_pos_weight=2.0,   <-- 데이터가 1:1이므로 인위적인 공포(가중치)는 필요 없다!!
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # 4. 모델 저장 (Vesper Java 연동용 JSON)
    model_path = os.path.join(settings.MODEL_DIR, "vortex_model_v1_balanced.json")
    model.save_model(model_path)
    
    # 5. 훈련 데이터 내재 평가
    y_pred = model.predict(X_train)
    logger.info("\n📊 [균형 데이터 학습 모델 - 내부 평가 지표]")
    print(confusion_matrix(y_train, y_pred))
    print(classification_report(y_train, y_pred))
    
    logger.success(f"✅ 균형 모델 저장 완료: {model_path}")

if __name__ == "__main__":
    train_vortex_balanced()
