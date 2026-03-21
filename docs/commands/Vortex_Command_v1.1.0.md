# Vortex 명령어 가이드 (Command Guide)
버전: v1.1.0 최종 업데이트: 2026-03-15

줄(JUL) 형님이 자주 사용하는 Vortex(볼텍스) 엔진 및 소피아(Sophia) API의 주요 명령어들을 모아둔 가이드입니다. 잊어버렸을 때 언제든 여기서 확인하세요! 🚀

## 1. 모델 학습 및 데이터 준비 (Training & Data)
### 모델 학습 실행 (XGBoost)
```bash
# Anvil의 Parquet 데이터를 읽어 Sophia v1 모델 학습
uv run python pipelines/vortex_train_premarket.py
```

### OOS(Out-of-Sample) 테스트
```bash
# 학습된 모델의 실전 성능 검증
uv run python pipelines/vortex_oos_test.py
```

## 2. 데이터 가공 및 덤프 (Data Export)
### Vesper용 Parquet 덤프 생성
```bash
# 분봉 파티셔닝 및 일봉 단일 파일 생성
uv run python pipelines/run_backtest_dump.py
```

### Vortex용 ML 피처 생성
```bash
# 기술적 지표 및 라벨링 포함된 Parquet 생성
uv run python pipelines/run_ml_pipeline.py
```

### 레짐(Regime) 지표 빌더
```bash
# QQQ 200일선 및 SQQQ 거래량 폭발 지표 생성
uv run python pipelines/regime_builder.py
```

## 3. 테스트 및 검증 (Test & Verify)
### 전체 데이터 무결성 전수조사
```bash
uv run python tests/full_survey.py
```

### 레짐 데이터 검증
```bash
uv run python tests/test_regime_data.py
```

### 로깅 시스템 테스트
```bash
uv run python tests/test_logger.py
```

## 4. 로그 및 DB 관리 (Maintenance)
### 실시간 로그 확인
```bash
# 최신 로그 파일 실시간 모니터링
tail -f logs/anvil-$(date +%Y-%m-%d).log
```

### DB 적재 건수 확인 (단축키)
```bash
./commands/check_db_counts.sh
```

### 직접 DB 접속 (psql)
```bash
PGPASSWORD=iotzu123 psql -h localhost -U postgres -d postgres
```

## 5. 기타 유용한 명령어
### 환경 변수 설정 (최초 실행 시)
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### 종목 리스트 확인
```bash
# app/core/config.py 에 정의된 TICKERS 확인
grep "TICKERS =" app/core/config.py
```

## 6. 소피아(Sophia) API 서비스
### Vortex 추론 서버 기동
```bash
# REST API 서버 가동 (Sophia Inference)
cd /Users/julicekim/iotzu/vortex
uv run uvicorn brain.api.vortex_api:app --host 127.0.0.1 --port 8000
```

### 1차 프리마켓 검증 수동 호출
```bash
# Anvil 수집 완료 후 Vesper 호출 전 수동 검증 실행 시 (오늘 날짜)
curl -X POST http://127.0.0.1:8000/pre-market

# 특정 날짜에 대한 과거 데이터 재분석 시
curl -X POST http://127.0.0.1:8000/pre-market/2026-03-13
```

---
**Tip:** 새로운 명령어가 추가되거나 변경되면 덱스(Dex)가 즉시 업데이트하겠습니다! 😊
