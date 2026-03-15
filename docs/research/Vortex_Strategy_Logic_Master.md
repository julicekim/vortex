# 📋 Vortex 전략 및 로직 마스터 (Strategy & Logic Master)
작성자: 덱스 (Dex), 준이 (Junie)
최종 업데이트: 2026-03-15

## 1. 개요 (Context)
이 문서는 **Vortex** AI 모델의 구조, 학습 전략, 추론 로직 및 성능 지표에 관한 모든 핵심 결정 사항을 통합 관리합니다.

## 2. 모델 아키텍처 및 학습 전략 (Model & Training)

### [2026-03-14] FastAPI 기반 REST API 전환
- **결정**: 무거운 XGBoost 라이브러리를 직접 서빙하는 대신, FastAPI 기반의 경량 REST API 연동 체계로 전환.
- **배경**: Vesper(Java) 엔진과의 결합도를 낮추고 추론 속도를 극대화하기 위함.
- **성과**: 17.5ms 이하의 초고속 응답 성능 및 100% 성공률 검증.

### [2026-03-13] 휩소(Whipsaw) 방어용 타겟 라벨링
- **전략**: 단순 수익률이 아닌, 손절선을 건드리지 않고 목표가에 도달하는지 판별하는 `target_whipsaw`를 학습 목표로 설정.
- **로직**: 미래 40분 이내에 1% 수익 도달 전 -0.5% 손실 발생 시 오답(0) 처리.

## 3. 피처 엔지니어링 및 전처리 (Feature Engineering)

### [2026-03-13] 종목 무관(Stationary) 피처 세트
- **핵심 피처**: `feat_sma_spread`, `feat_vwap_spread`, `feat_natr_14`, `RSI_14`.
- **원칙**: 주가의 절대치에 오염되지 않도록 모든 가격 지표를 현재가 대비 비율로 정규화하여 학습.

## 4. 성능 지표 및 검증 (Evaluation)
- **핵심 지표**: Precision (고점 오탐 방지), F1-Score (학습 균형).
- **검증**: `pipelines/vortex_oos_test.py`를 통한 Out-of-Sample 테스트 수행.

## 5. 히스토리 및 아카이브 (History)
- 과거의 모델 성능 리포트 및 상세 수정 내역은 [Archive_v1_Historical_Reports.md](../history/archive/Archive_v1_Historical_Reports.md)를 참조하십시오.
