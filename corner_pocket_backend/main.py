from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from corner_pocket_backend.core.config import settings
from corner_pocket_backend.api.routes import router as api_router

corner_pocket_backend = FastAPI(title="Corner-Pocket API", version="0.1.0")

corner_pocket_backend.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Uses your existing config!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@corner_pocket_backend.get("/health")
def health():
    return {"ok": True}

corner_pocket_backend.include_router(api_router, prefix="/api/v1")
