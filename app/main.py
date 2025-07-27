"""
🌟 Polaris System Detection API - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import main_routes, polaris_routes
from app.config.settings import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )

    # Include routers
    app.include_router(main_routes.router)
    app.include_router(polaris_routes.router)
    
    # Include legacy compatibility routes if enabled (disabled by default)
    if settings.legacy_compatible:
        from app.api import transformer_lab_routes
        app.include_router(transformer_lab_routes.router)

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    print("🌟 ================================")
    print("🌟  POLARIS SYSTEM DETECTION API")
    print("🌟 ================================")
    print(f"🚀 Starting Polaris on http://{settings.host}:{settings.port}")
    print(f"📖 Docs: http://{settings.host}:{settings.port}{settings.docs_url}")
    
    if settings.legacy_compatible:
        print(f"🔄 Legacy compatibility: http://{settings.host}:{settings.port}{settings.legacy_prefix}")
    
    print("🌟 ================================")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level
    ) 