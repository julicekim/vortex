import pytest
import pandas as pd
from fastapi.testclient import TestClient
from brain.api.vortex_api import app
from unittest.mock import MagicMock, patch

# 1. API 테스트 클라이언트 설정
client = TestClient(app)

def test_health_check():
    """
    [Vortex API] 서버 상태 확인 엔드포인트 테스트
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_endpoint_success():
    """
    [Vortex API] /predict 엔드포인트 정상 작동 테스트
    """
    payload = {
        "vol_surge_ratio": 1.5,
        "vwap_dist_pct": 0.5,
        "mins_from_open": 30.0,
        "atr_compression_ratio": 0.8
    }
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    result = response.json()
    assert "danger" in result
    assert "probability" in result
    assert isinstance(result["danger"], bool)
    assert 0.0 <= result["probability"] <= 1.0

def test_predict_endpoint_invalid_input():
    """
    [Vortex API] /predict 엔드포인트 잘못된 입력값 테스트 (Validation Check)
    """
    # 필수 필드 누락
    payload = {
        "vol_surge_ratio": 1.5
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422 # Unprocessable Entity

@patch("brain.api.vortex_api.db_client")
@patch("brain.api.vortex_api.os.path.exists")
def test_pre_market_validation_flow(mock_exists, mock_db):
    """
    [Vortex API] /pre-market 엔드포인트 로직 흐름 테스트
    - DB 조회 및 추론 로직이 정상적으로 호출되는지 확인 (Mocking)
    """
    # A. Mocking 설정
    mock_exists.return_value = True # sync_status.txt 존재함
    
    # 1. 전일 종가 데이터 Mock
    mock_daily_data = pd.DataFrame([
        {"ticker": "AAPL", "prev_close": 150.0, "date": "2026-03-14"},
        {"ticker": "NVDA", "prev_close": 800.0, "date": "2026-03-14"}
    ])
    
    # 2. 당일 프리마켓 데이터 Mock (UTC 기준)
    # API 내부에서 UTC로 인식 후 NY 시간(04:00~09:30)으로 변환함. 
    # UTC 10:00 -> NY 05:00 (EST 기준 -5)
    mock_pre_data = pd.DataFrame([
        {"ticker": "AAPL", "time": "2026-03-15 10:00:00", "open": 151.0, "high": 152.0, "low": 150.5, "close": 151.5, "volume": 1000},
        {"ticker": "NVDA", "time": "2026-03-15 10:00:00", "open": 810.0, "high": 820.0, "low": 805.0, "close": 815.0, "volume": 5000}
    ])
    
    # db_client.fetch_as_df 호출 시 가상 데이터 반환
    mock_db.fetch_as_df.side_effect = [mock_daily_data, mock_pre_data]
    
    # B. API 호출
    with patch("brain.api.vortex_api.vortex_model") as mock_model:
        # 모델 추론 결과 Mock (XGBoost predict_proba 형식)
        import numpy as np
        mock_model.predict_proba.return_value = np.array([[0.8, 0.2]]) # 1(위험)일 확률 0.2
        
        response = client.post("/pre-market")
        
    # C. 검증
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["analyzed_count"] > 0
    
    # DB 적재 함수가 호출되었는지 확인
    assert mock_db.upsert_intelligence.called
    logger_call_args = mock_db.upsert_intelligence.call_args[0][0]
    assert len(logger_call_args) > 0
    assert "ticker" in logger_call_args[0]
    assert "is_danger" in logger_call_args[0]

@patch("brain.api.vortex_api.db_client")
@patch("brain.api.vortex_api.os.path.exists")
def test_pre_market_validation_with_date(mock_exists, mock_db):
    """
    [Vortex API] /pre-market/{date} 엔드포인트 날짜 지정 테스트
    """
    target_date = "2026-03-10"
    mock_exists.return_value = True
    
    # 가상 데이터 (지정된 날짜 기반)
    mock_daily_data = pd.DataFrame([{"ticker": "AAPL", "prev_close": 150.0, "date": "2026-03-09"}])
    mock_pre_data = pd.DataFrame([{"ticker": "AAPL", "time": f"{target_date} 10:00:00", "open": 151.0, "high": 152.0, "low": 150.5, "close": 151.5, "volume": 1000}])
    
    mock_db.fetch_as_df.side_effect = [mock_daily_data, mock_pre_data]
    
    with patch("brain.api.vortex_api.vortex_model") as mock_model:
        import numpy as np
        mock_model.predict_proba.return_value = np.array([[0.9, 0.1]])
        
        # 날짜를 포함하여 호출
        response = client.post(f"/pre-market/{target_date}")
        
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    
    # DB 적재 시 timestamp가 지정된 날짜인지 확인
    insert_args = mock_db.upsert_intelligence.call_args[0][0]
    assert insert_args[0]["timestamp"].strftime('%Y-%m-%d') == target_date

def test_pre_market_validation_invalid_date():
    """
    [Vortex API] /pre-market/{date} 잘못된 날짜 형식 테스트
    """
    response = client.post("/pre-market/invalid-date")
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]

@patch("brain.api.vortex_api.db_client")
@patch("brain.api.vortex_api.os.path.exists")
def test_pre_market_batch_validation(mock_exists, mock_db):
    """
    [Vortex API] /pre-market/batch 엔드포인트 기간별 일괄 분석 테스트
    """
    # 2일치 데이터 시뮬레이션 (2026-03-02 월요일, 2026-03-03 화요일)
    # 2026-03-01은 일요일이므로 skip됨
    start_date = "2026-03-01"
    end_date = "2026-03-03"
    
    mock_exists.return_value = True
    
    # 각 날짜별로 2회씩 DB 조회 발생 (전일종가, 당일분봉)
    # 03-02 (월), 03-03 (화) -> 총 4회
    mock_daily_1 = pd.DataFrame([{"ticker": "AAPL", "prev_close": 150.0}])
    mock_pre_1 = pd.DataFrame([{"ticker": "AAPL", "time": "2026-03-02 10:00:00", "open": 151.0, "high": 152.0, "low": 150.5, "close": 151.5, "volume": 1000}])
    
    mock_daily_2 = pd.DataFrame([{"ticker": "AAPL", "prev_close": 151.5}])
    mock_pre_2 = pd.DataFrame([{"ticker": "AAPL", "time": "2026-03-03 10:00:00", "open": 152.0, "high": 153.0, "low": 151.5, "close": 152.5, "volume": 1200}])
    
    mock_db.fetch_as_df.side_effect = [mock_daily_1, mock_pre_1, mock_daily_2, mock_pre_2]
    
    with patch("brain.api.vortex_api.vortex_model") as mock_model:
        import numpy as np
        mock_model.predict_proba.return_value = np.array([[0.9, 0.1]])
        
        payload = {
            "start_date": start_date,
            "end_date": end_date
        }
        response = client.post("/pre-market/batch", json=payload)
        
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["days_processed"] == 2 # 03-02, 03-03만 처리됨
    assert result["total_analyzed"] == 2
    
    # DB Upsert가 2회 호출되었는지 확인
    assert mock_db.upsert_intelligence.call_count == 2

def test_pre_market_batch_invalid_range():
    """
    [Vortex API] /pre-market/batch 잘못된 날짜 범위 테스트
    """
    payload = {
        "start_date": "2026-03-05",
        "end_date": "2026-03-01"
    }
    response = client.post("/pre-market/batch", json=payload)
    assert response.status_code == 400
    assert "start_date cannot be after end_date" in response.json()["detail"]
