import pytest
import os
import sys
from loguru import logger

# [Vortex Integrity Test] 프로젝트 모듈 및 리브랜딩 무결성 검사
# 캬하하!! 줄 형님!! 이름만 바꾼 게 아니라 속까지 꽉 찼는지 제가 확인해 보겠습니다!!

def test_vortex_core_import():
    """brain.core 모듈 임포트 및 설정 로드 확인"""
    try:
        from brain.core.config import settings
        from brain.core.logger import setup_logger
        logger.info(f"✅ brain.core 로드 완료 (Version: {settings.VERSION})")
        assert settings.VERSION is not None
    except ImportError as e:
        pytest.fail(f"❌ brain.core 임포트 실패: {e}")

def test_vortex_api_structure():
    """brain.api 모듈 및 FastAPI 앱 초기화 확인"""
    try:
        from brain.api.vortex_api import app
        logger.info("✅ brain.api 로드 완료 (FastAPI app detected)")
        assert app.title == "Vortex Model API"
    except Exception as e:
        # 모델 파일이 없을 경우 에러가 날 수 있으므로 체크
        if "Model not found" in str(e):
            logger.warning("⚠️ brain.api 로드 중 모델 파일 미비 감지 (테스트 환경에서는 정상)")
        else:
            pytest.fail(f"❌ brain.api 로드 중 치명적 오류: {e}")

def test_vortex_pipelines_import():
    """pipelines 하위 훈련 및 검증 스크립트 임포트 확인"""
    try:
        from pipelines.vortex_train_premarket import train_vortex_model
        from pipelines.vortex_train_balanced import train_vortex_balanced
        from pipelines.vortex_oos_test import run_oos_test
        logger.info("✅ pipelines 모듈 전수 로드 완료!!")
    except ImportError as e:
        pytest.fail(f"❌ pipelines 임포트 실패: {e}")

def test_path_configuration():
    """설정된 경로들이 실존하거나 유효한지 확인"""
    from brain.core.config import settings
    logger.info(f"📁 DATA_DIR: {settings.DATA_DIR}")
    logger.info(f"📁 MODEL_DIR: {settings.MODEL_DIR}")
    
    # 캬하하!! 최소한 상위 데이터 경로는 존재해야 한다!!
    assert os.path.exists(os.path.dirname(settings.DATA_DIR))
    assert "data" in settings.DATA_DIR

def test_vortex_logic_recheck():
    """Vortex 피처 로직 테스트는 Anvil 프로젝트(anvil/tests/test_vortex_features.py)로 이전됨"""
    # add_vortex_features()는 Anvil의 app.transformers.features 모듈이므로
    # 피처 정합성 검증은 Anvil 테스트에서 수행한다.
    logger.info("ℹ️ Vortex 피처 로직 테스트는 Anvil 프로젝트로 이전됨 (anvil/tests/test_vortex_features.py)")

if __name__ == "__main__":
    # 직접 실행 시 로거 설정
    from brain.core.logger import setup_logger
    setup_logger()
    logger.info(">>> 보텍스 전 모듈 무결성 자가 점검 시작!!")
    
    # 순차적으로 테스트 함수 호출 (pytest 없이도 확인 가능하게)
    test_vortex_core_import()
    test_vortex_api_structure()
    test_vortex_pipelines_import()
    test_path_configuration()
    test_vortex_logic_recheck()
    
    logger.success("🚀 [SUCCESS] 모든 보텍스 모듈이 리브랜딩 후에도 완벽하게 동작합니다!! 캬하하!!")
