from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.api import router

app = FastAPI(title=settings.app_name, version=settings.app_version,
    description="SONORA music discovery and playback orchestration API",
    docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix=settings.api_prefix, tags=["SONORA v1"])

@app.get("/")
async def root():
    return {"name": settings.app_name, "version": settings.app_version,
            "docs": "/docs", "api": settings.api_prefix}

@app.get("/health")
async def health():
    return {"status": "ok"}
