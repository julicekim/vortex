import os
import sys
from loguru import logger
from brain.core.config import settings

def setup_logger():
    """
    Loguru를 사용하여 Vortex 로깅 시스템을 초기화한다.
    - logs 폴더 내에 vortex-YYYY-MM-DD.log 파일로 저장
    - Rolling 정책 적용 (10MB 단위로 새로운 파일 생성, 최대 30일 보관)
    - 준이(Junie)의 v1.0.0 표준 준수
    """
    # 로그 디렉토리 생성
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # 기존 핸들러 제거 (중복 로깅 방지)
    logger.remove()
    
    # 1. 콘솔 출력 설정
    logger.add(
        sys.stderr, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 2. 파일 출력 설정 (준이의 v1.0.0 표준 패턴)
    log_file_path = os.path.join(settings.LOG_DIR, "vortex-{time:YYYY-MM-DD}.log")
    logger.add(
        log_file_path,
        rotation="10 MB",     
        retention="30 days",  
        compression="zip",    
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        encoding="utf-8"
    )
    
    logger.info(f"Vortex Logging system initialized. Logs are saved in: {log_file_path}")
