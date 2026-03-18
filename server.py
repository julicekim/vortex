import uvicorn
import sys
import os

# Vortex 루트를 PYTHONPATH에 추가
sys.path.insert(0, os.path.dirname(__file__))

from brain.api.vortex_api import app  # noqa: F401

if __name__ == "__main__":
    uvicorn.run(
        "brain.api.vortex_api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
