from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import Optional


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
    
    # PostgreSQL - Conexión a la base de datos principal
    POSTGRES_SERVER: str = Field(default="localhost", env="POSTGRES_SERVER")
    POSTGRES_PORT: str = Field(default="5432", env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="mysecret", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="tornado-se-dev", env="POSTGRES_DB")
    DATABASE_URL: Optional[str] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v, values) -> str:
        if v:
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{values.get('POSTGRES_DB')}"
    
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
