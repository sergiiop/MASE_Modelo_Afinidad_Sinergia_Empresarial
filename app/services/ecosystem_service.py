import json
import logging
import uuid
from typing import Dict, List, Optional, Any

from app.models.ecosystem import EcosystemConfig
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import Ecosystem, Company


class EcosystemService:
    """
    Servicio para gestionar las configuraciones de ecosistemas empresariales.
    Permite a cada dueño de ecosistema configurar sus propios pesos para los factores
    de compatibilidad y otras configuraciones específicas.
    """
    _instance = None
    _ecosystems_cache = {}
    
    def __new__(cls):
        """Implementación de patrón Singleton para asegurar una sola instancia."""
        if cls._instance is None:
            cls._instance = super(EcosystemService, cls).__new__(cls)
        return cls._instance
    
    def get_default_config(self) -> EcosystemConfig:
        """
        Obtiene una configuración por defecto para ecosistemas.
        
        Returns:
            Configuración por defecto
        """
        return EcosystemConfig(
            id="default",
            name="Configuración por defecto",
            description="Configuración por defecto para ecosistemas sin configuración específica",
            peso_afinidad=1.0,
            peso_sinergia=1.0,
            peso_empleados=1.0,
            peso_ciudad=1.0,
            peso_tamaño=1.0,
            peso_sector=1.0,
            max_matches_per_company=10,
            min_match_score=0.0,
            active=True
        )


# Instancia global del servicio
ecosystem_service = EcosystemService()


def get_ecosystem_service() -> EcosystemService:
    """
    Función para obtener la instancia del servicio de ecosistemas.
    Útil para inyección de dependencias en FastAPI.
    """
    return ecosystem_service
