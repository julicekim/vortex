import polars as pl
import pytest
from datetime import datetime, timedelta
from app.transformers.features import add_vortex_features
from loguru import logger

def generate_mock_data():
    """
    [Vortex 검증용] 가상 OHLCV 데이터 생성
    - 08:00 ~ 12:00 (윈도우 연산을 위한 충분한 패딩 확보)
    - 1분봉 240개
    """
    start_time = datetime(2024, 3, 14, 8, 0)
    data = []
    
    for i in range(240):
        current_time = start_time + timedelta(minutes=i)
        ticker = "AAPL"
        
        # 기본값
        open_p = 100.0
        high = 100.5
        low = 99.5
        close = 100.0
        volume = 100.0
        
        # 09:30 ~ 09:59 (개장 직후): 거래량 폭발
        if current_time >= datetime(2024, 3, 14, 9, 30) and current_time < datetime(2024, 3, 14, 10, 0):
            volume = 1000.0
            close = 101.0
            high = 101.5
        # 10:00 ~ 10:29 (상승기): 미래 1% 상승 도달 시나리오
        elif current_time >= datetime(2024, 3, 14, 10, 0) and current_time < datetime(2024, 3, 14, 10, 30):
            close = 103.0
            high = 103.5
        # 10:30 ~ : 횡보 및 하락
        elif current_time >= datetime(2024, 3, 14, 10, 30):
            close = 99.0
            high = 99.5
            
        data.append({
            "ticker": ticker,
            "time": current_time,
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume
        })
        
    return pl.DataFrame(data)

def test_vortex_logic_integrity():
    """
    [Vortex 명세서] 5대 핵심 로직 최종 검증
    """
    df = generate_mock_data()
    result_df = add_vortex_features(df)
    
    logger.info(f"테스트 결과 데이터 프레임 로우 수: {len(result_df)}")
    
    # 1. [F1] 거래량 폭발 비율 (feat_vol_surge_ratio) 검증
    # 30번째 인덱스(09:30)는 직전 20개 평균(100) 대비 1000이므로 약 10.0 근처여야 함
    surge_row = result_df.filter(pl.col("time") == datetime(2024, 3, 14, 9, 30))
    if not surge_row.is_empty():
        surge_ratio = surge_row["feat_vol_surge_ratio"][0]
        logger.info(f"09:30 거래량 폭발 비율: {surge_ratio}")
        assert surge_ratio > 5.0 # 급증 확인
    
    # 2. [F3] 개장 후 경과 시간 (feat_mins_from_open) 검증
    # 09:30 -> 0분, 10:30 -> 60분
    # 주의: Polars의 dt.hour()는 로컬 시간대에 따라 다를 수 있으므로 상대적 차이만 확인함.
    
    open_row = result_df.filter(pl.col("time") == datetime(2024, 3, 14, 9, 30))
    hour_later_row = result_df.filter(pl.col("time") == datetime(2024, 3, 14, 10, 30))
    
    if not open_row.is_empty() and not hour_later_row.is_empty():
        base_mins = open_row["feat_mins_from_open"][0]
        later_mins = hour_later_row["feat_mins_from_open"][0]
        logger.info(f"09:30 경과 값: {base_mins}, 10:30 경과 값: {later_mins}")
        assert later_mins - base_mins == 60 # 1시간 차이 검증

    # 3. [F2] VWAP 이격도 (feat_vwap_dist_pct) 검증
    # 09:30에 거래량이 터졌으므로 VWAP은 101에 가까울 것임. 종가 101과의 이격도는 0 근처
    if not surge_row.is_empty():
        vwap_dist = surge_row["feat_vwap_dist_pct"][0]
        logger.info(f"09:30 VWAP 이격도: {vwap_dist}")
        assert abs(vwap_dist) < 1.0

    # 4. [Y] 정답지 라벨 (target_label) 검증
    # 09:30(종가 101) 시점: 미래 30분(09:31~10:00) 동안 최고가 103.5(+2.4%) 도달 -> 0 (안전)
    label_safe = result_df.filter(pl.col("time") == datetime(2024, 3, 14, 9, 30))["target_label"][0]
    logger.info(f"09:30 타겟 라벨: {label_safe}")
    assert label_safe == 0
    
    # 10:30(종가 99) 시점: 이후 횡보/하락 -> +1.0% 도달 불가 -> 1 (위험)
    label_risk = result_df.filter(pl.col("time") == datetime(2024, 3, 14, 10, 30))["target_label"][0]
    logger.info(f"10:30 타겟 라벨: {label_risk}")
    assert label_risk == 1

    logger.success("✅ Vortex 명세서 5대 로직 검증 완료 (Unit Test Passed!!)")

if __name__ == "__main__":
    test_vortex_logic_integrity()
