# 🛠️ Project Anvil: 상세 기술 로드맵 (Detailed Roadmap)

"데이터는 속도와 무식함(Brute-force)으로 찢는 거야!" - 덱스(Dex)

---

## 📌 Phase 1: 추출기(Extractor) 고도화 - "진공청소기 강화"

### 1.1 Alpaca API v2 Multi-symbol 조회 최적화
- **현재**: 단일 심볼(AAPL) 조회 수준의 프로토타입.
- **목표**: S&P 500 전 종목 또는 사용자 정의 관심 종목 리스트에 대한 동시 비동기 요청 처리.
- **기술적 디테일**:
    - `aiohttp.ClientSession`을 재사용하여 TCP 연결 오버헤드 최소화.
    - `asyncio.gather`를 활용한 병렬 요청 처리 및 `asyncio.Semaphore`를 이용한 Rate Limit(분당 200회) 준수 로직 구현.
    - `page_token` 기반의 자동 페이지네이션 루프 구현으로 누락 데이터 방지.

### 1.2 에러 핸들링 및 재시도 전략
- HTTP 429(Too Many Requests) 및 5xx 에러 발생 시 지수 백오프(Exponential Back-off) 적용.
- 네트워크 단절 시 상태 저장 및 마지막 성공 지점부터 재개(Resume) 기능 검토.

---

## 📌 Phase 2: 제련소(Transformer) 확장 - "모루의 정밀도"

### 2.1 Polars 기반 기술적 지표(Technical Indicators) 엔진 구축
- 소피아(Sophia) 누님이 요청할 ML 피처(Feature)를 Polars의 벡터 연산으로 계산.
- **주요 계산 항목**:
    - 이동평균선 (SMA, EMA): `rolling_mean` 활용.
    - RSI (Relative Strength Index): `diff`, `clip` 연산을 통한 노이즈 없는 고속 계산.
    - ATR (Average True Range): 변동성 측정을 위한 고저차 계산 로직.
    - 거래량 가중 평균 가격 (VWAP): 누적 합계(`cumsum`) 기반 실시간 연산.

### 2.2 데이터 무결성 검증(Validation) 강화
- `Great Expectations` 또는 Polars 자체 스키마 검증 기능을 활용하여 결측치, 이상치(Outlier), 타임스탬프 역전 현상 자동 탐지.
- 타임존(UTC) 고정 및 정밀도(Decimal 12, 4) 캐스팅 규칙 엄격 적용.

---

## 📌 Phase 3: 적재기(Loader) 구현 - "망치의 파괴력"

### 3.1 로컬 Postgres 초고속 벌크 인서트
- **기존**: 단건 또는 소량 `INSERT`.
- **목표**: `psycopg2`의 `execute_values` 또는 `copy_expert`를 활용한 초당 만 단위 이상의 데이터 적재.
- **기술적 디테일**:
    - `ON CONFLICT (timestamp, symbol) DO NOTHING` (또는 UPDATE) 구문을 통한 멱등성(Idempotency) 보장.
    - 커넥션 풀링(Connection Pooling) 적용으로 DB 부하 관리.

### 3.2 DuckDB 연동 및 로컬 캐싱
- Postgres 적재 전, 로컬 `duckdb` 또는 `parquet` 파일로 임시 저장하여 네트워크 장애 시 데이터 유실 방지 및 빠른 분석 환경 제공.

---

## 📌 Phase 4: 운영 및 자동화 - "엔진 자동 가동"

### 4.1 파이프라인 스케줄링
- `GitHub Actions` 또는 `Cron`을 활용하여 매일 미 증시 마감 후 자동 실행 환경 구축.
- 실패 시 `Loguru` JSON 로그 기반 알림 시스템 연동.

### 4.2 백테스트 전용 덤프(Exporters)
- Vesper(Java) 및 Vortex(ML) 연동을 위한 대용량 `minute_candles.parquet` 생성 로직 최적화.

---

## 📌 Phase 5: 전략적 협업 (Dex & Sophia) - "지능형 데이터 서빙"

### 5.1 주간 Value 후보 발굴 파이프라인 (Sunday Pipeline)
- **일정**: 매주 일요일 가동.
- **로직**: 일봉 데이터를 풀스캔하여 저평가 구간 또는 특정 패턴(예: 역배열 돌파)을 보이는 '이번 주의 Value 후보 Top 10' 선정.
- **적재**: 선정된 심볼 리스트를 Postgres `value_tier_symbols` 테이블에 자동 업데이트.

### 5.2 종목 성격별 피처 차별화 (Dynamic Features)
- **전략**: 일반 종목과 ValueTier 종목의 지표 반응 속도 차이 인정.
- **협업**: 앤빌(Anvil)이 종목 등급 정보를 Vortex(ML)에 넘겨주면, 소피아(Sophia) 누님이 전용 RSI 임계치(예: Value 종목은 60 이상 시 과매수)를 적용하도록 설계.

---

## 📌 Phase 6: 다이내믹 유니버스 (Screener) - "종목은 걸러지는 것이다"

### 6.1 이오츠/카포의 레이더망 (screener.py)
- **일정**: 매월 말일 또는 매일 밤 가동.
- **필터링 조건**:
    - **거래대금(Capo's Rule)**: 최근 20일 평균 거래대금 $1,000만 이상 (유동성 확보).
    - **변동성(Capo's Rule)**: 최근 14일 ATR 비율 3% 이상 (단타 수익 구간 확보).
- **로직**: 시장 전체 종목 스캔 후 상위 100개 종목 추출.

### 6.2 동적 유니버스 관리 (dynamic_universe)
- **적재**: Postgres `dynamic_universe` 테이블에 날짜별 타겟 심볼 저장.
- **연동**: ETL 추출기 가동 시 하드코딩된 리스트 대신 `dynamic_universe`를 참조하여 데이터 낭비 최소화.

---

## 📅 타임라인 (Timeline)
1. **Week 1**: Phase 1 (추출기) & Phase 2 (기초 지표) 완성.
2. **Week 2**: Phase 3 (벌크 적재) & 멱등성 검증 완료.
3. **Week 3**: Phase 4 (자동화) 및 전체 통합 테스트.

캬하하!! 줄 형님!! 이 로드맵대로라면 자바 충들이 DTO 설계할 때 우린 이미 전 종목 1분봉 데이터 싹 다 긁어서 DB에 꽂아버릴 수 있습니다!! 🚀🔥
