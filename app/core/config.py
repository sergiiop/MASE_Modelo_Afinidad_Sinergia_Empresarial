from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional
from urllib.parse import quote_plus
import sys
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Configuración del microservicio de matching utilizando variables de entorno.
    """
    # Configuración general
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DATA_DIR: str = Field(default="./data", env="DATA_DIR")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    DEFAULT_LIMIT: int = Field(default=100, env="DEFAULT_LIMIT")
    
    # PostgreSQL - Conexión a la base de datos principal (requeridas)
    POSTGRES_SERVER: str = Field(..., env="POSTGRES_SERVER")
    POSTGRES_PORT: str = Field(..., env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    DATABASE_URL: Optional[str] = None
    
    @field_validator("POSTGRES_SERVER", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", mode="before")
    def validate_postgres_vars(cls, v, info):
        if not v:
            error_msg = f"La variable de entorno {info.field_name} es requerida para la conexión a PostgreSQL"
            logger.error(error_msg)
            sys.exit(1)
        return v
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v, info) -> str:
        if v:
            return v
        password = quote_plus(str(info.data.get('POSTGRES_PASSWORD')))
        return f"postgresql://{info.data.get('POSTGRES_USER')}:{password}@{info.data.get('POSTGRES_SERVER')}:{info.data.get('POSTGRES_PORT')}/{info.data.get('POSTGRES_DB')}"
    
    class Config:
        env_prefix = ""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignorar variables adicionales en el archivo .env


# Instancia global de configuración
settings = Settings()


def get_settings() -> Settings:
    """
    Función para obtener la configuración actual.
    """
    return settings
