from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Vortex 시스템 버전
    VERSION: str = "1.0.0"

    # [Paths] 데이터 저장 경로 설정 (Anvil과 공유!!)
    # Anvil이 제련한 데이터를 Vortex가 직접 흡수한다!!
    DATA_DIR: str = "/Users/julicekim/iotzu/data"
    PROCESSED_DIR: str = "/Users/julicekim/iotzu/data/processed"
    ML_FEATURES_DIR: str = "/Users/julicekim/iotzu/data/ml_features"
    
    # Vortex 전용 경로
    BASE_DIR: str = "/Users/julicekim/iotzu/vortex"
    LOG_DIR: str = "/Users/julicekim/iotzu/vortex/logs"
    MODEL_DIR: str = "/Users/julicekim/iotzu/vortex/vortex/models/saved"

    # [Training] 학습 관련 설정
    BATCH_SIZE: int = 32
    EPOCHS: int = 50
    LEARNING_RATE: float = 0.001
    RANDOM_SEED: int = 42

    # [Universe] 심볼 관리 (Anvil과 동일하게 유지하여 정합성 확보!!)
    NASDAQ_TICKERS: list[str] = [
        'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META',
        'TSLA', 'NVDA', 'AMD', 'NFLX', 'AVGO',
        'SMCI', 'ARM'
    ]

    # 환경 변수 우선순위: 시스템 환경 변수 > .env 파일
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
