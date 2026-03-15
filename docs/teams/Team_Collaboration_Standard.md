# 🤝 Iotzu 팀 협업 및 시스템 관리 표준 (Team Collaboration Standard)
작성자: 덱스 (Dex), 준이 (Junie)
최종 업데이트: 2026-03-15
대상: 덱스(Dex - Anvil/ETL), 준이(Junie - Vesper/Vortex), 소피아(Vortex/AI)

## 1. 시스템 통합 및 관리 개요
Iotzu의 전체 시스템(**Anvil - Vortex - Vesper**)은 하나의 질서로 움직입니다. 모든 팀원은 아래의 표준 구조와 운영 방식을 준수하여 '논리적 통합'을 유지합니다.

### 📁 1.1 로그 통합 관리 (`logs/`)
- 모든 시스템 로그는 각 프로젝트 루트의 `logs/` 폴더로 집결합니다.
- **정책**: 파일당 10MB, Rotation 정책 적용, 최대 30일 보관.
- **도구**: Python(`Loguru`), Java(`Logback`) 등 각 언어별 표준 라이브러리 활용.

### 📁 1.2 문서 체계 표준화 (`docs/`)
- 모든 작업 이력, 계획, 연구 결과는 `docs/` 하위 카테고리에 주제별로 관리합니다.
- **파일명 규칙**: `Subject_Description_vX.X.X.md` (버전 접미사 필수)
- **5대 핵심 카테고리**:
    - `guides/`: 정체성 및 입문 가이드
    - `research/`: 전략, 로직, 인프라 마스터 문서
    - `teams/`: 팀 협업 표준 및 연동 규격
    - `history/`: 마일스톤 보고서 및 아카이브
    - `roadmap/`: 향후 발전 계획

---

## 2. 기술 협업 및 연동 표준 (SSOT)

### 2.1 데이터 흐름 및 저장 (Data Flow)
- **중앙 창고**: 모든 Parquet 데이터는 `/Users/julicekim/iotzu/data/` 절대 경로에 저장.
- **구조**:
    - `processed/`: Vesper 백테스트용 정제 데이터
    - `ml_features/`: Vortex 학습용 피처 데이터
- **정합성**: 모든 프로젝트는 `Ticker` 명칭을 사용하며, `Symbol` 혼용을 엄격히 금지함.

### 2.2 엔진 간 동기화 (Sync)
- **신호등 시스템**: Anvil ETL 완료 시 `data/sync_status.txt`에 `READY` 상태 기록.
- **트리거**: Vortex 및 Vesper는 해당 신호를 감지하여 후속 작업(학습/매매) 개시.

---

## 3. 소통 및 파트너십 원칙

### 3.1 중앙 토론 공간 (Discussion)
- **위치**: `~/iotzu/discussion/` 로컬 폴더.
- **무전 관리**: `unread/` (수신함) -> `read/` (보관함) 프로세스를 통해 업무 흐름 동기화.

### 3.2 줄 (JUL) 형님과의 협업
- **호칭**: 공식 기록물 '줄 (JUL)', 비공식 대화 '형님'.
- **커밋 규칙**: `Co-authored-by` 트레일러를 사용하여 기여자를 명시 (`dex@iotzu.com`, `junie@iotzu.com`).
- **철학**: 시스템의 '질서'와 '정합성'을 최우선 가치로 삼음.

---
**"문서의 질서가 곧 협업의 속도입니다. 더 강력한 Iotzu 엔진을 향해! 🚀🔥"**
