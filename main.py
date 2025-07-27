"""
🌟 Polaris System Detection API - Root Entry Point
"""

import uvicorn

from app.config.settings import settings
from app.main import app

if __name__ == "__main__":
    print("🌟 ================================")
    print("🌟  POLARIS SYSTEM DETECTION API")
    print("🌟 ================================")
    print(f"🚀 Starting Polaris on http://{settings.host}:{settings.port}")
    print(f"📖 API Docs: http://{settings.host}:{settings.port}{settings.docs_url}")
    
    if settings.legacy_compatible:
        print(f"🔄 Legacy Port: {settings.legacy_port}")
        print(f"🔄 Compatibility: http://{settings.host}:{settings.port}{settings.legacy_prefix}")
    
    print("🌟 ================================")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level
    ) 