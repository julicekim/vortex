# Vortex BUG TRACKER

> 최종 업데이트: 2026-03-21
> 리뷰어: Jack (시니어 코드 리뷰어)

---

## 범례

| 등급 | 의미 |
|------|------|
| 🔴 BUG | 확인된 버그 — 수정 필요 |
| ⚠️ SUSPECT | 설계 의도 확인 필요 — 버그 가능성 |
| ✅ RESOLVED | 수정 완료 |

| 영향도 | 의미 |
|--------|------|
| CRITICAL | 모델 학습/추론 결과 전체 오염 |
| HIGH | 특정 피처/라벨/API 왜곡 |
| MEDIUM | 잠재적 장애 또는 데이터 품질 저하 |
| LOW | 코드 품질/유지보수성 |

---

## 채번 현황

| 구분 | 마지막 번호 | 다음 사용 |
|------|------------|-----------|
| BUG  | BUG-V11    | BUG-V12   |
| S    | (없음)     | S-V1      |

---

## 🔴 BUG (Open)

(현재 Open 버그 없음)

---

## ⚠️ SUSPECT (Open)

(현재 Open SUSPECT 없음)

---

## ✅ RESOLVED

> 잭 코드 리뷰 기반 8건 수정 (2026-03-21, 커밋 `2128451`)
> 추가 2건 수정 (2026-03-21, 커밋 `3134bd6`)

| 번호 | 내용 | 수정일 | 비고 |
|------|------|--------|------|
| BUG-V1 | `vortex_train_balanced.py` inf/NaN 클리닝 누락 | 2026-03-21 | 프로덕션 모델 파이프라인 — 오염 데이터 학습 위험 |
| BUG-V2 | `test_vortex_setup.py` 임포트 경로 `vortex→brain` 수정 | 2026-03-21 | 패키지 리브랜딩 누락 |
| BUG-V3 | `test_vortex_api.py` batch 역전 날짜 테스트 기대값 수정 | 2026-03-21 | start > end 검증 테스트 |
| BUG-V4 | `test_vortex_logic.py` Anvil로 이전 | 2026-03-21 | Anvil 의존성 분리 — `anvil/tests/test_vortex_features.py` |
| BUG-V5 | `config.py` ALL_TICKERS `set()→dict.fromkeys()` 순서 보장 | 2026-03-21 | set()은 순서 미보장 — 재현성 위험 |
| BUG-V6 | `vortex_api.py` DEBUG 로그 `logger.info→logger.debug` 정리 | 2026-03-21 | 프로덕션 로그 오염 방지 |
| BUG-V7 | 학습 파이프라인 모델 메타데이터(`_meta.json`) 저장 추가 | 2026-03-21 | OOS 테스트 피처 자동 선택 지원 |
| BUG-V8 | `vortex_train_balanced.py` Validation Set + early_stopping 추가 | 2026-03-21 | 과적합 방지 — 10라운드 조기 종료 |
| — | `pre-market/batch` API + 테스트 삭제 | 2026-03-21 | 미사용 엔드포인트 정리 |
| — | `vortex_oos_test.py` OOS 경로 고정 + `_meta.json` 기반 피처 선택 | 2026-03-21 | suffix 경로 오류 + 피처 불일치 수정 |
| BUG-V9 | `vortex_train.py` Validation Set + early_stopping 누락 | 2026-03-21 | balanced만 적용되고 원본 누락 — 과적합 방지 브레이크 없음 |
| BUG-V10 | `vortex_train.py` → `vortex_train_premarket.py` 리네임 | 2026-03-21 | 프리마켓 피처 포함 학습 스크립트 — 파일명으로 용도 구분 |
| BUG-V11 | `vortex_train_balanced.py` 훈련 기간 `2018→2017` 통일 | 2026-03-21 | 2017 데이터 존재하므로 두 스크립트 훈련 기간 일치시킴 |

---

*"모델의 실력은 데이터의 품질에서 시작된다. 오염된 입력은 어떤 알고리즘도 구원하지 못한다." — Jack*
*마지막 업데이트: 2026-03-21 by codegg (잭 리뷰 8건 + 추가 2건 반영, 트래커 신규 생성)*
