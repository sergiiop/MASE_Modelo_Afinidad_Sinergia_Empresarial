from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

# Crear el motor de base de datos
SQLALCHEMY_DATABASE_URL = get_settings().DATABASE_URL

# Motor síncrono
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


# Dependencia para obtener la sesión de base de datos
def get_db():
    """
    Dependencia para obtener una sesión de base de datos.
    Para usar con FastAPI Depends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
