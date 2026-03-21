from brain.core.config import settings
from brain.core.logger import setup_logger
from loguru import logger
import os

def test_vortex_setup():
    # 1. Logger 초기화
    setup_logger()
    logger.info("Vortex setup test started!!")

    # 2. Config 로드 확인
    logger.info(f"Vortex Version: {settings.VERSION}")
    logger.info(f"Data Dir: {settings.DATA_DIR}")
    
    assert settings.VERSION == "1.0.0"
    assert "iotzu/data" in settings.DATA_DIR
    
    # 3. 로그 파일 생성 확인
    log_files = [f for f in os.listdir(settings.LOG_DIR) if f.startswith("vortex-")]
    logger.info(f"Generated log files: {log_files}")
    assert len(log_files) > 0
    
    logger.success("Vortex setup test passed!! 캬하하!! 🚀🔥")

if __name__ == "__main__":
    test_vortex_setup()
