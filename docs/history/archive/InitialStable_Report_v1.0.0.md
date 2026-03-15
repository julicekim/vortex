# v1.0.0_InitialStable_Report.md

준이(Junie)의 **시스템 문서 및 로그 관리 표준화 명세서(v1.0.0)**를 준수하여 작성된 Anvil 초기 안정화 버전 리포트입니다.

### 🚀 Summary
- Anvil 시스템의 초기 안정화 버전(v1.0.0)이 완성되었습니다.
- 클라우드(Supabase)에서 로컬 Postgres 환경으로의 이관 및 데이터 수집/정제 파이프라인의 전면적인 구조 개선이 완료되었습니다.
- 준이의 표준 명세서에 따른 디렉토리 구조 세분화 및 로깅 정책 고도화가 적용되었습니다.

### 🛠️ 주요 변경 사항 (Changes)

#### 1. 시스템 관리 표준 (Management Standard)
- **문서 체계**: `docs/history/`, `docs/roadmap/`, `docs/research/`, `docs/checkpoint/`, `docs/reports/`로 분류 체계 확립.
- **로깅 정책**: `logs/anvil-YYYY-MM-DD.i.log` 형식의 롤링 정책 도입 (30일 보관, 10MB 제한).
- **자동 레포트**: `pipelines/run_daily_etl.py` 실행 시 `docs/reports/daily_etl_check.md`에 결과 자동 기록 기능 추가.

#### 2. 인프라 및 설정 (Infrastructure & Config)
- **DB 이관**: Supabase 연결을 제거하고 로컬 PostgreSQL(Port: 5432) 기반으로 모든 로더(`PostgresLoader`)와 엑스포터를 전환했습니다.
- **경로 중앙화**: 데이터 저장 경로(`/Users/julicekim/iotzu/data/`) 및 로그 경로를 `app/core/config.py`로 집중화하여 관리 효율성을 높였습니다.
- **절대 경로**: `~/` 단축 표기를 제거하고 `/Users/julicekim/iotzu/` 절대 경로 체계로 통일했습니다.

#### 3. 데이터 유니버스 & ETL (Universe & ETL)
- **심볼 이원화**: `NASDAQ_TICKERS`(매매용), `NON_NASDAQ_TICKERS`(다변화용), `REGIME_TICKERS`(관측용)로 심볼 관리 체계를 세분화했습니다.
- **통합 파이프라인**: 모든 ETL 스크립트가 중앙 설정의 `ALL_TICKERS`를 참조하도록 일원화했습니다.
- **히스토리 수집**: 2000년부터 2026년 3월 13일까지의 대량 데이터 수집이 가능하도록 `--group` 파라미터 및 `sleep` 로직을 강화했습니다.

#### 4. 레짐 지표 및 분석 (Regime & Analysis)
- **Regime Builder**: QQQ 200일 SMA(거시) 및 SQQQ 거래량 Surge Ratio(미시) 계산 엔진을 신규 구축했습니다.
- **Parquet Exporter**: Vesper 엔진용 심볼별 파티셔닝 덤프와 Vortex 엔진용 ML 피처 덤프 엔진을 최적화했습니다.

### ✅ 검증 완료 (Verification)
- `tests/full_survey.py`를 통한 25개 종목 데이터 무결성 전수 조사 통과.
- `tests/test_dump_integrity.py`를 통한 Parquet 덤프 엔진 검증 완료.
- `tests/test_regime_data.py`를 통한 지표 계산 로직 검증 완료.
- `app/core/logger.py`의 롤링 정책 명세서 준수 여부 확인.
