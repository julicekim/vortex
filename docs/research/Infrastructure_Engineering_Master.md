# 🏗️ Vortex 인프라 및 기술 마스터 (Infrastructure & Engineering Master)
작성자: 덱스 (Dex), 준이 (Junie)
최종 업데이트: 2026-03-15

## 1. 개요 (Context)
이 문서는 **Vortex** 모델의 학습 파이프라인, GPU/CPU 최적화, API 아키텍처 및 시스템 인프라에 관한 모든 기술적 레슨을 기록합니다.

## 2. API 및 서빙 아키텍처 (API & Serving)

### [2026-03-14] FastAPI 비동기 추론 엔진
- **기술**: `asyncio` 기반의 FastAPI 비동기 서빙 구현.
- **배경**: Vesper 엔진의 대량 추론 요청을 병목 없이 처리하기 위해 도입.
- **성과**: 1,000회 연속 호출 스트레스 테스트 통과 (평균 17.5ms 응답).

## 3. 학습 파이프라인 및 최적화 (Pipeline & Optimization)

### [2026-03-13] Polars 기반 데이터 로더
- **기술**: 학습용 대용량 Parquet 데이터를 읽기 위해 **Polars** 도입.
- **이유**: Pandas 대비 수배 빠른 데이터 로딩 및 전처리 속도 확보.
- **OOM**: 메모리 부족 방지를 위해 학습 시 불필요한 원시 컬럼은 과감히 제거하고 피처만 추출하여 학습기에 주입.

## 4. 로깅 및 모니터링 (Operations)

### [2026-03-14] 로깅 Rolling 정책
- **정책**: `Loguru`를 기반으로 10MB 단위 Rotation 정책 적용.
- **위치**: 모든 로그는 `vortex/logs/` 중앙 폴더에 집약 관리.

## 5. 시행착오 및 복구 (Post-mortem)
- 과거의 구체적인 에러 수정 이력 및 긴급 점검 리포트는 [Archive_v1_Historical_Reports.md](../history/archive/Archive_v1_Historical_Reports.md)를 참조하십시오.
