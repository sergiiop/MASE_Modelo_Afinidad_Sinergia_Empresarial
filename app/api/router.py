from fastapi import APIRouter

from app.api.ecosystem_matches_endpoints import router as ecosystem_matches_router

# Router principal que incluye todos los demás routers
api_router = APIRouter()

# Incluir solo el router de ecosystem_matches_endpoints
api_router.include_router(
    ecosystem_matches_router,
    prefix="/api/v1",
    tags=["ecosystem-matches"]
)
