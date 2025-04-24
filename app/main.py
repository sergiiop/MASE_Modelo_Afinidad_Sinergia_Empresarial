from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.api.router import api_router
from app.db.database import Base, engine

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title="MASE Matching Microservice",
    description="Microservicio para el cálculo de matches entre empresas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(api_router)

# Evento de inicio para crear las tablas de la base de datos
# @app.on_event("startup")
# async def startup_db_client():
#     logger.info("Creando tablas en la base de datos si no existen...")
#     Base.metadata.create_all(bind=engine)
#     logger.info("Tablas creadas correctamente.")

# Ruta de inicio
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "MASE Matching Microservice is running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
