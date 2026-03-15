# 🌪️ Vortex (볼텍스): 소피아(Sophia) 누님 전용 ML 학습 엔진 (v1.0.0)

와하하!! 줄 형님의 앤빌(Anvil)이 찢어발긴 데이터를 먹고 자라는 초고속 ML 학습 엔진 **볼텍스(Vortex)**입니다!! 

---

## 🏷️ 시스템 관리 (Standard Management)
준이(Junie)의 **시스템 문서 및 로그 관리 표준화 명세서(v1.0.0)**를 준수합니다.

- **현재 버전**: `v1.0.0`
- **📂 문서 구조 (Docs Index)**:
    - [🧠 덱스의 기억 (Vault)](docs/history/Dexs_Memory_Vault.md): Vortex 엔진의 영혼과 파트너십 가이드 [MASTER]
    - [📋 전략 및 로직 마스터](docs/research/Vortex_Strategy_Logic_Master.md): 모델 아키텍처 및 학습 전략 [STRATEGY]
    - [🏗️ 인프라 및 기술 마스터](docs/research/Infrastructure_Engineering_Master.md): API 서빙 및 학습 최적화 [INFRA]
    - [🤝 팀 협업 표준](docs/teams/Team_Collaboration_Standard.md): Iotzu 팀 공통 협업 규격 [TEAM]
    - [📜 작업 이력 및 아카이브](docs/history/Archive_v1_Historical_Reports.md): 과거 모델 리포트 통합본 [HISTORY]
    - [🚀 명령어 가이드](docs/commands/Vortex_Command_v1.1.0.md): 볼텍스 운영 커맨드 보관소
    - [🗺️ 로드맵 v1.0.0](docs/roadmap/Vortex_Roadmap_v1.0.0.md): 볼텍스 진화 계획
- **📝 로깅 정책**: `logs/` 디렉토리에 10MB Rolling 정책 적용 (Loguru)

---

## 🏗️ 볼텍스 아키텍처 (Archi's Design)
볼텍스는 앤빌에서 덤프한 최고급 Parquet 파일을 흡수하여 소피아 누님의 뇌(Model)를 강화하는 역할을 합니다!!

- **vortex/datasets**: 앤빌의 `sophia_train_v1.parquet`을 읽어 PyTorch Dataset으로 변환!!
- **vortex/models**: 소피아 누님이 설계한 딥러닝/부스팅 모델들의 보금자리!!
- **vortex/trainers**: 손실 함수(Loss), 최적화(Optimizer)를 담당하는 훈련소!!
- **pipelines/run_train.py**: 실제 학습을 가동하는 메인 스위치!!
- **vortex/core**: 중앙 제어 설정 및 로깅 시스템!!

---

## 🚀 가동 준비!! (Setup)
```bash
# 1. 가상환경 구축 및 의존성 주입 (PyTorch, LightGBM 등 정예 부대!!)
uv sync

# 2. 소피아 누님 모델 학습 개시!! (명령어 가이드 참조)
uv run python pipelines/run_train.py
```

## 🤝 앤빌(Anvil)과의 연동
- 앤빌에서 `uv run python pipelines/run_ml_pipeline.py`를 실행하여 학습용 데이터를 연성하세요!!
- 생성된 Parquet 파일은 `/Users/julicekim/iotzu/data/` 경로에서 볼텍스가 직접 흡수합니다!! 캬하하!!

줄 형님! 소피아 누님의 지능이 폭발하는 순간을 기대해 주십시오!! 가자가자!! 🚀🔥 와하하!!
