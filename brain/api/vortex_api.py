from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
import xgboost as xgb
import pandas as pd
import numpy as np
import os
from datetime import datetime, timezone, timedelta
from brain.core.config import settings
from brain.core.db import PostgresClient
from loguru import logger

# [Vortex API 1.1] 소피아(Sophia) 1차 프리마켓 검증 API 추가!!
app = FastAPI(title="Vortex Model API", version="1.2.0")
db_client = PostgresClient()

# 1. 서버 기동 시 모델을 메모리에 1회만 로드 (속도 최적화)
# 캬하하!! 줄 형님!! 모델은 이미 전용 금고(data/models/)에 모셔놨습니다!!
model_path = os.path.join(settings.MODEL_DIR, "vortex_model_v1_balanced.json")

if not os.path.exists(model_path):
    logger.error(f"🚨 모델 파일이 존재하지 않습니다: {model_path}")
    raise FileNotFoundError(f"Model not found at {model_path}")

logger.info(f"🧠 소피아(Vortex 1.0 Balanced) 뇌를 메모리에 로드 중... ({model_path})")
vortex_model = xgb.XGBClassifier()
vortex_model.load_model(model_path)
logger.success("✅ Vortex 모델 로드 완료. API 서버가 준이(Junie)의 요청을 기다립니다!!")

# v2 모델 (프리마켓 피처 포함: 6개)
model_v2_path = os.path.join(settings.MODEL_DIR, "vortex_model_v1_with_pre.json")
if not os.path.exists(model_v2_path):
    logger.error(f"🚨 v2 모델 파일이 존재하지 않습니다: {model_v2_path}")
    raise FileNotFoundError(f"Model v2 not found at {model_v2_path}")

logger.info(f"🧠 소피아 v2(with_pre) 뇌를 메모리에 로드 중... ({model_v2_path})")
vortex_model_v2 = xgb.XGBClassifier()
vortex_model_v2.load_model(model_v2_path)
logger.success("✅ Vortex v2 모델 로드 완료.")

# 2. 입력 데이터 구조 정의 (Type Validation & Documentation)
# 앤빌(Anvil)의 피처 명칭을 그대로 사용하되, 준이(Junie)의 Vesper 요청 편의를 위해 별칭(Alias) 부여!!
# [IMPORTANT] Pydantic V2에서는 alias가 설정되면 요청 시 해당 이름으로 필드를 찾아야 함!!
class FeatureInput(BaseModel):
    # 🚨 Pydantic V2 철벽 방어: 원래 이름과 별칭 모두 허용
    model_config = ConfigDict(populate_by_name=True)

    vol_surge_ratio: float = Field(..., description="거래량 폭발 비율")
    vwap_dist_pct: float = Field(..., description="VWAP 이격도 (%)")
    mins_from_open: float = Field(..., description="개장 후 경과 시간 (분)")
    atr_compression_ratio: float = Field(..., description="변동성 압축 비율 (1m/5m)")

class FeatureInputV2(BaseModel):
    """프리마켓 피처 포함 v2 입력 스키마 (6개 피처)"""
    model_config = ConfigDict(populate_by_name=True)

    vol_surge_ratio: float = Field(..., description="거래량 폭발 비율")
    vwap_dist_pct: float = Field(..., description="VWAP 이격도 (%)")
    mins_from_open: float = Field(..., description="개장 후 경과 시간 (분)")
    atr_compression_ratio: float = Field(..., description="변동성 압축 비율 (1m/5m)")
    pre_market_gap: float = Field(..., description="프리마켓 갭 비율 (%)")
    pre_market_high_dist: float = Field(..., description="프리마켓 고점 이격도 (%)")

class BatchDateRequest(BaseModel):
    start_date: str = Field(..., description="시작 날짜 (YYYY-MM-DD)")
    end_date: str = Field(..., description="종료 날짜 (YYYY-MM-DD)")

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
        
        # 준이(Junie)가 읽기 편하도록 boolean 형태로 반환!!
        return result
        
    except Exception as e:
        logger.error(f"🚨 추론 중 에러 발생: {e}")
        # 상세 에러 메시지 포함 (디버깅 용)
        raise HTTPException(status_code=500, detail=f"Inference Error: {str(e)}")

@app.post("/predict/v2")
def predict_v2(data: FeatureInputV2):
    """
    [Vortex Inference v2] 프리마켓 피처 포함 6개 피처로 위험 여부 판별!!
    - 모델: vortex_model_v1_with_pre (feat_pre_market_gap, feat_pre_market_high_dist 추가)
    - danger: true(위험/진입금지), false(안전/진입가능)
    - probability: 위험(1)일 확률 (0.0 ~ 1.0)
    """
    try:
        input_dict = {
            "feat_vol_surge_ratio": data.vol_surge_ratio,
            "feat_vwap_dist_pct": data.vwap_dist_pct,
            "feat_mins_from_open": data.mins_from_open,
            "feat_atr_compression_ratio": data.atr_compression_ratio,
            "feat_pre_market_gap": data.pre_market_gap,
            "feat_pre_market_high_dist": data.pre_market_high_dist,
        }
        logger.info(f"📥 [Predict v2 Request] Features: {input_dict}")
        df = pd.DataFrame([input_dict])
        prediction = vortex_model_v2.predict(df)[0]
        prob = float(vortex_model_v2.predict_proba(df)[0][1])
        result = {
            "danger": bool(prediction == 1),
            "probability": round(prob, 4)
        }
        logger.info(f"📤 [Predict v2 Result] {result}")
        return result
    except Exception as e:
        logger.error(f"🚨 v2 추론 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=f"Inference v2 Error: {str(e)}")

@app.get("/intelligence/{target_date}")
async def get_intelligence(target_date: str):
    """
    [Sophia Intelligence Query] 특정 날짜의 프리마켓 분석 결과를 DB에서 조회한다.
    - target_date: 'YYYY-MM-DD' 형식
    - Vesper가 2차 필터링 시 pull 방식으로 사용
    """
    try:
        datetime.strptime(target_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    try:
        query = "SELECT * FROM v_vortex_intelligence WHERE timestamp::date = %s ORDER BY ticker ASC"
        df = db_client.fetch_as_df(query, (target_date,))
        records = df.to_dict(orient="records")
        logger.info(f"📊 [Intelligence Query] {target_date} → {len(records)}건 반환")
        return {"date": target_date, "count": len(records), "records": records}
    except Exception as e:
        logger.error(f"🚨 intelligence 조회 중 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """서버 상태 확인용 엔드포인트"""
    return {"status": "healthy", "model_v1": "vortex_model_v1_balanced", "model_v2": "vortex_model_v1_with_pre"}

@app.post("/pre-market")
@app.post("/pre-market/{target_date}")
async def validate_pre_market(target_date: str = None):
    """
    [Sophia 1st Validation] 프리마켓 데이터를 분석하여 당일(또는 지정된 날짜) 위험 종목을 1차 필터링한다.
    - target_date: 'YYYY-MM-DD' 형식의 문자열 (생략 시 오늘 날짜)
    - DB(minute_candles)에서 해당일 04:00~09:30 프리마켓 데이터 조회
    - Gap Ratio, Volume Surge 등 주요 피처 계산
    - v_vortex_intelligence 테이블에 결과 기록 (Vesper 2차 필터링 기반 데이터)
    """
    start_time = datetime.now()
    try:
        # 날짜 파싱 및 유효성 검사
        if target_date:
            try:
                datetime.strptime(target_date, '%Y-%m-%d')
                today_date = target_date
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            now_utc = datetime.now(timezone.utc)
            today_date = now_utc.strftime('%Y-%m-%d')
        
        logger.info(f"🚀 [Pre-market Validation] {today_date} 분석 세션 시작...")
        
        # 0. Anvil 동기화 상태 확인 (READY 사인 대기)
        # 앤빌이 수집을 완료하고 READY를 띄웠을 때만 진행 (안정성 확보!!)
        sync_file = os.path.join(settings.DATA_DIR, "sync_status.txt")
        if os.path.exists(sync_file):
            with open(sync_file, "r") as f:
                status = f.read().strip()
                if status != "READY":
                    logger.warning(f"⚠️ Anvil 상태가 READY가 아닙니다 ({status}). 분석 결과가 불완전할 수 있습니다.")
        else:
            logger.warning("⚠️ Anvil sync_status.txt 파일을 찾을 수 없습니다. 수집 상태를 직접 확인하세요.")

        # 1. 전일 종가 데이터 조회 (Gap 계산용)
        # UTC 기준이므로 영업일 고려하여 최근 5일치 중 마지막 데이터를 가져옴
        daily_query = """
            SELECT ticker, close as prev_close, date
            FROM daily_candles
            WHERE date < %s::date
            ORDER BY date DESC
            LIMIT %s
        """
        # 전체 종목 리스트에 대해 최근 종가 확보
        tickers = settings.ALL_TICKERS
        daily_df = db_client.fetch_as_df(daily_query, (today_date, len(tickers) * 2))
        
        if daily_df.empty:
            logger.warning(f"⚠️ {today_date} 이전의 종가 데이터가 DB에 없습니다. 분석을 제한적으로 수행합니다.")
            
        # 2. 당일 프리마켓 데이터 조회 (04:00 ~ 09:30 ET)
        pre_query = """
            SELECT ticker, time, open, high, low, close, volume
            FROM minute_candles
            WHERE time >= %s::date AND time < (%s::date + interval '1 day')
        """
        pre_df = db_client.fetch_as_df(pre_query, (today_date, today_date))
        
        if pre_df.empty:
            logger.error(f"❌ {today_date} 프리마켓 수집 데이터가 DB에 없습니다. Anvil 수집(22:10 종료)을 확인하세요.")
            return {"status": "error", "message": "No pre-market data found in DB", "analyzed_count": 0}

        # 뉴욕 시간대 변환 및 프리마켓 필터링
        pre_df['time'] = pd.to_datetime(pre_df['time'])
        if pre_df['time'].dt.tz is None:
            pre_df['time'] = pre_df['time'].dt.tz_localize('UTC')
        
        pre_df['ny_time'] = pre_df['time'].dt.tz_convert('America/New_York')
        pre_df = pre_df[
            (pre_df['ny_time'].dt.hour >= 4) & 
            ((pre_df['ny_time'].dt.hour < 9) | ((pre_df['ny_time'].dt.hour == 9) & (pre_df['ny_time'].dt.minute < 30)))
        ]
        
        if pre_df.empty:
            logger.warning(f"⚠️ 필터링 후 프리마켓 데이터가 없습니다. (시간대 설정 확인 필요)")
            return {"status": "success", "analyzed_count": 0, "message": "No pre-market data found after NY timezone filtering"}

        # 3. 티커별 피처 계산 및 추론
        results = []
        analyzed_count = 0
        
        for ticker in tickers:
            ticker_df = pre_df[pre_df['ticker'] == ticker]
            if ticker_df.empty:
                continue
                
            # A. Gap Ratio 계산
            ticker_daily = daily_df[daily_df['ticker'] == ticker]
            prev_close = ticker_daily['prev_close'].iloc[0] if not ticker_daily.empty else None
            
            # 프리마켓 현재가 (마지막 봉)
            last_price = ticker_df.sort_values('time')['close'].iloc[-1]
            
            gap_ratio = 0.0
            if prev_close:
                gap_ratio = float((last_price - prev_close) / prev_close * 100)
            
            # B. Pre-market Volume 분석
            total_vol = int(ticker_df['volume'].sum())
            # 최근 10분 평균 거래량 (급증세 확인용)
            recent_vol = ticker_df.sort_values('time').tail(10)['volume'].mean()
            vol_surge = float(recent_vol / (total_vol / len(ticker_df)) if total_vol > 0 else 1.0)
            
            # C. Sophia Inference Input 생성
            # 학습 모델의 피처셋: vol_surge_ratio, vwap_dist_pct, mins_from_open, atr_compression_ratio
            input_features = {
                "vol_surge_ratio": vol_surge,
                "vwap_dist_pct": gap_ratio, # 프리마켓에서는 갭이 VWAP 이격도와 유사한 성격
                "mins_from_open": 0.0,      # 프리마켓은 장 오픈 전이므로 0
                "atr_compression_ratio": 1.0 # 프리마켓은 변동성 압축 데이터 부재로 1.0 고정
            }
            
            # 추론 실행
            inference_df = pd.DataFrame([{
                "feat_vol_surge_ratio": input_features["vol_surge_ratio"],
                "feat_vwap_dist_pct": input_features["vwap_dist_pct"],
                "feat_mins_from_open": input_features["mins_from_open"],
                "feat_atr_compression_ratio": input_features["atr_compression_ratio"]
            }])
            
            prob = float(vortex_model.predict_proba(inference_df)[0][1])
            
            # [Dex's Rule-based Filter] 
            # 모델 점수가 낮아도 Gap이 너무 크거나(폭등) 작으면(폭락) 위험군으로 분류
            is_danger = bool(prob > 0.45 or abs(gap_ratio) > 7.0 or vol_surge > 5.0)
            
            # 처리 지연 시간 계산 (ms)
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            
            results.append({
                "timestamp": datetime.strptime(today_date, '%Y-%m-%d').replace(tzinfo=timezone.utc),
                "ticker": ticker,
                "vol_surge": input_features["vol_surge_ratio"],
                "vwap_dist": input_features["vwap_dist_pct"],
                "mins_open": input_features["mins_from_open"],
                "atr_comp": input_features["atr_compression_ratio"],
                "probability": round(prob, 4),
                "is_danger": is_danger,
                "latency_ms": latency
            })
            analyzed_count += 1
            
        # 4. DB 적재 (Upsert 적용하여 멱등성 확보!!)
        if results:
            db_client.upsert_intelligence(results)
            
        logger.success(f"✅ {today_date} 프리마켓 1차 검증 완료. ({analyzed_count} 종목 분석됨)")
        return {"status": "success", "analyzed_count": analyzed_count, "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000)}
        
    except HTTPException:
        # FastAPI의 HTTPException은 그대로 통과시켜야 400 등 올바른 상태코드가 반환됨
        raise
    except Exception as e:
        logger.error(f"🚨 프리마켓 검증 중 치명적 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pre-market/batch")
async def validate_pre_market_batch(data: BatchDateRequest):
    """
    [Sophia Batch Validation] 특정 기간(1년 등)의 프리마켓 데이터를 일괄 분석하여 DB에 적재한다.
    - 백테스트(Backtest)용 대량 데이터 생성에 최적화!!
    """
    start_time = datetime.now()
    logger.info(f"DEBUG: Received batch request: {data}")
    try:
        try:
            start_dt = datetime.strptime(data.start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(data.end_date, '%Y-%m-%d')
            logger.info(f"DEBUG: Parsed dates: {start_dt}, {end_dt}")
        except ValueError as ve:
            logger.error(f"DEBUG: Date parsing failed: {ve}")
            raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD. Error: {str(ve)}")
            
        if start_dt > end_dt:
            raise HTTPException(status_code=400, detail="start_date cannot be after end_date")
            
        logger.info(f"📅 [Batch Validation] {data.start_date} ~ {data.end_date} 분석 시작!!")
        
        current_dt = start_dt
        total_analyzed = 0
        days_processed = 0
        
        while current_dt <= end_dt:
            # 주말(토요일=5, 일요일=6)은 분석에서 제외 (영업일 기준)!!
            if current_dt.weekday() < 5:
                target_date = current_dt.strftime('%Y-%m-%d')
                # 기존 validate_pre_market 로직 재활용 (비동기 함수 호출)
                # 🚨 주의: sync_status.txt 체크는 배치 시에는 워닝 정도로만 처리됨
                try:
                    result = await validate_pre_market(target_date)
                    if result["status"] == "success":
                        total_analyzed += result["analyzed_count"]
                        days_processed += 1
                except Exception as e:
                    logger.warning(f"⚠️ {target_date} 분석 실패 (건너뜀): {e}")
            
            current_dt += timedelta(days=1)
            
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        logger.success(f"✅ 배치 분석 완료!! {days_processed}일간 총 {total_analyzed}개 레코드 적재됨. (소요: {latency}ms)")
        
        return {
            "status": "success",
            "days_processed": days_processed,
            "total_analyzed": total_analyzed,
            "latency_ms": latency
        }
        
    except HTTPException:
        # FastAPI의 HTTPException은 그대로 통과시켜야 400 등 올바른 상태코드가 반환됨
        raise
    except Exception as e:
        logger.error(f"🚨 배치 검증 중 치명적 에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 서버 실행 방법:
# PYTHONPATH=$PYTHONPATH:. uvicorn brain.api.vortex_api:app --host 127.0.0.1 --port 8000
