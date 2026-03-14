import os
import polars as pl
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix
from brain.core.config import settings
from loguru import logger

def train_vortex_model():
    """
    [Vortex 1.0] 소피아(Sophia) 누님의 보수적 XGBoost 분류기 학습
    - 훈련 데이터(2018~2023) 25개 종목을 병합하여 학습시킨다.
    - OOS(2024~2025) 데이터는 절대 접근 금지!! (이오츠 샌님 지침)
    """
    logger.info(">>> [Phase 2] Vortex 1.0 모델 훈련 프로세스 가동!!")
    
    # 1. 훈련 데이터 경로 설정 (기존 sophia_train_v1 하위 train_2018_2023 폴더)
    train_dir = os.path.join(settings.ML_FEATURES_DIR, "sophia_train_v1/train_2018_2023")
    
    if not os.path.exists(train_dir):
        logger.error(f"훈련 데이터 폴더가 없습니다: {train_dir}")
        return

    parquet_files = [os.path.join(train_dir, f) for f in os.listdir(train_dir) if f.endswith('.parquet')]
    
    if not parquet_files:
        logger.error("병합할 Parquet 파일이 없습니다!!")
        return

    logger.info(f"📦 {len(parquet_files)}개의 TICKER 훈련 데이터를 병합 중... (2018-2023)")
    
    # Polars의 광속 병합 가동!!
    df_list = []
    for f in parquet_files:
        df_list.append(pl.read_parquet(f))
    
    df_train = pl.concat(df_list)
    logger.info(f"총 {len(df_train)}행의 대규모 훈련 데이터셋 로드 완료!!")

    # 2. 피처(X)와 정답지(Y) 분리 
    # [Anvil 엔진 규격 반영] 명세서의 명칭과 앤빌의 피처 접두어(feat_)를 맞춘다.
    feature_cols = [
        "feat_vol_surge_ratio", 
        "feat_vwap_dist_pct", 
        "feat_mins_from_open", 
        "feat_atr_compression_ratio"
    ]
    target_col = "target_label"

    # 모델 학습을 위해 Pandas로 변환 (XGBoost 호환성)
    X_train = df_train.select(feature_cols).to_pandas()
    y_train = df_train.select(target_col).to_pandas().values.ravel()

    # 3. XGBoost 모델 세팅 (소피아의 과적합 방지 보수적 파라미터)
    logger.info("🧠 소피아(Sophia) 누님의 신경망 학습 시작... 과적합 방지 룰 적용!!")
    
    model = xgb.XGBClassifier(
        max_depth=3,              # 얕은 트리: 소설 쓰지 마라!!
        learning_rate=0.05,       # 보수적인 학습 속도
        n_estimators=100,         # 트리 개수 제한
        scale_pos_weight=2.0,     # 위험(1) 라벨 가중치 2배!! (보수적 차단이 목적이다!!)
        random_state=42,
        n_jobs=-1,                # M1 칩 코어 풀가동!! 캬하하!!
        use_label_encoder=False,
        eval_metric='logloss'
    )

    # 4. 모델 훈련
    model.fit(X_train, y_train)

    # 5. 훈련 데이터 내재 평가 (참고용)
    y_pred = model.predict(X_train)
    
    logger.info("\n📊 [훈련 데이터 내부 평가 지표 (Train In-Sample)]")
    conf_matrix = confusion_matrix(y_train, y_pred)
    class_report = classification_report(y_train, y_pred)
    
    print("\nConfusion Matrix:")
    print(conf_matrix)
    print("\nClassification Report:")
    print(class_report)

    # 6. 모델 저장 (Vesper Java 엔진 호환용 JSON 포맷)
    model_path = os.path.join(settings.MODEL_DIR, "vortex_model_v1.json")
    model.save_model(model_path)
    
    logger.success(f"✅ Vortex 모델 저장 완료: {model_path}")
    logger.info("이제 이 모델은 주니(Junie)의 Vesper 엔진에서 필터로 작동하게 될 거야!!")

if __name__ == "__main__":
    train_vortex_model()
