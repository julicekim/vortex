from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

_VORTEX_ROOT = Path(__file__).parent.parent.parent  # ~/iotzu/vortex
_IOTZU_ROOT = _VORTEX_ROOT.parent                   # ~/iotzu

class Settings(BaseSettings):
    # Vortex 시스템 버전
    VERSION: str = "1.0.0"

    # [Paths] 데이터 저장 경로 설정 (Anvil과 공유!!)
    # Anvil이 제련한 데이터를 Vortex가 직접 흡수한다!!
    DATA_DIR: str = str(_IOTZU_ROOT / "data")
    PROCESSED_DIR: str = str(_IOTZU_ROOT / "data" / "processed")
    ML_FEATURES_DIR: str = str(_IOTZU_ROOT / "data" / "ml_features")

    # Vortex 전용 경로
    BASE_DIR: str = str(_VORTEX_ROOT)
    LOG_DIR: str = str(_VORTEX_ROOT / "logs")
    MODEL_DIR: str = str(_IOTZU_ROOT / "data" / "models")  # Anvil이 만든 모델 금고와 통합!!

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

    NON_NASDAQ_TICKERS: list[str] = [
        'LLY', 'UNH', 'JPM', 'GS', 'GE', 'CAT', 'LMT', 'XOM', 'WMT', 'COST'
    ]

    REGIME_TICKERS: list[str] = ["QQQ", "PSQ", "SQQQ"]

    @property
    def ALL_TICKERS(self) -> list[str]:
        return list(set(self.NASDAQ_TICKERS + self.NON_NASDAQ_TICKERS + self.REGIME_TICKERS))

    # Postgres 데이터베이스 연결 설정 (Anvil과 동일하게 유지!!)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "iotzu123"
    DB_NAME: str = "postgres"

    # 환경 변수 우선순위: 시스템 환경 변수 > .env 파일
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
