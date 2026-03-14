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

## 2. 모델 학습 및 가동
- **소피아 누님 모델 학습 개시!!**
  ```bash
  uv run python pipelines/run_train.py
  ```
- **특정 에포크(Epoch)만 테스트 학습**
  ```bash
  uv run python pipelines/run_train.py --epochs 1
  ```

## 3. 로그 및 데이터 확인
- **Vortex 실시간 로그 확인**
  ```bash
  tail -f logs/vortex-2026-03-14.log
  ```
- **앤빌이 제련한 Parquet 데이터 경로 확인**
  ```bash
  ls -lh /Users/julicekim/iotzu/data/ml_features/sophia_train_v1/
  ```

## 4. 기타 유틸리티
- **컴파일 및 문법 검사**
  ```bash
  uv run ruff check .
  ```

줄 형님! 새로운 명령어가 추가될 때마다 덱스가 빛의 속도로 업데이트하겠습니다!! 🚀🔥 와하하!!
