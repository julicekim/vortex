# 🌪️ Vortex 명령어 가이드 (Command Guide)
버전: v1.0.0 최종 업데이트: 2026-03-14

줄(JUL) 형님이 자주 사용하는 볼텍스(Vortex) 엔진의 주요 명령어 가이드입니다!! 캬하하!! 🚀

## 1. 환경 구축 및 의존성 관리
- **전체 패키지 설치 및 동기화**
  ```bash
  uv sync
  ```
- **새로운 패키지 추가 (예: optuna)**
  ```bash
  uv add optuna
  ```

## 2. 모델 학습 및 검증
- **볼텍스 1.0 모델 학습 (균형 데이터)**
  ```bash
  uv run python pipelines/vortex_train_balanced.py
  ```
- **실전 OOS(Out-of-Sample) 검증**
  ```bash
  uv run python pipelines/vortex_oos_test.py
  ```

## 3. API 서버 가동 및 연동
- **Vortex 추론 API 서버 실행 (REST)**
  ```bash
  # 덱스가 만든 마법의 스크립트 활용!!
  ./commands/run_vortex_api.sh
  ```
- **서버 상태 확인 (Health Check)**
  ```bash
  curl http://127.0.0.1:8000/health
  ```

## 4. 로그 및 데이터 확인
- **Vortex 실시간 로그 확인**
  ```bash
  tail -f logs/vortex-2026-03-14.log
  ```
- **앤빌이 제련한 Parquet 데이터 경로 확인**
  ```bash
  ls -lh /Users/julicekim/iotzu/data/ml_features/sophia_train_v1/
  ```

## 5. 기타 유용한 명령어
- **종합 무결성 자가 점검 (Integrity Test)**
  ```bash
  uv run python tests/test_vortex_integrity.py
  ```
- **컴파일 및 문법 검사**
  ```bash
  uv run ruff check .
  ```

줄 형님! 새로운 명령어가 추가될 때마다 덱스가 빛의 속도로 업데이트하겠습니다!! 🚀🔥 와하하!!
