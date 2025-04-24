from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid

class EcosystemConfig(BaseModel):
    """
    Configuración específica para un ecosistema empresarial.
    Cada ecosistema puede tener sus propios pesos para los factores de compatibilidad.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único del ecosistema en formato UUID")
    name: str
    description: Optional[str] = None
    
    # Pesos para los factores de compatibilidad
    peso_afinidad: float = 1.0
    peso_sinergia: float = 1.0
    peso_empleados: float = 1.0
    peso_ciudad: float = 1.0
    peso_tamaño: float = 1.0
    peso_sector: float = 1.0

    # Empresa dueña del ecosistema (opcional)
    company_id: Optional[str] = None
    
    # Configuración adicional específica del ecosistema
    max_matches_per_company: int = 10
    min_match_score: float = 0.0
    active: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "name": "Ecosistema Tecnológico",
                "description": "Ecosistema de empresas del sector tecnológico",
                "peso_afinidad": 1.2,
                "peso_sinergia": 1.5,
                "peso_empleados": 0.8,
                "peso_ciudad": 0.7,
                "peso_tamaño": 0.6,
                "peso_sector": 1.3,
                "company_id": "company-123",
                "max_matches_per_company": 15,
                "min_match_score": 5.0,
                "active": True
            }
        }


class EcosystemMatchConfig(BaseModel):
    """
    Configuración para el cálculo de matches en un ecosistema específico.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único de la configuración en formato UUID")
    config: EcosystemConfig
