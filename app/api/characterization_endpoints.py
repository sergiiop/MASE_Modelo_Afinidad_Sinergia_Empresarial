from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from app.db.database import get_db
from app.services.characterization_service import CharacterizationService

router = APIRouter()

class ItemCharacterization(BaseModel):
    id: str
    titulo: str
    key: str
    estado: bool
    orden: int
    es_requerido: bool
    tipo: str
    is_default: bool
    configuration: Dict = None

@router.get("/ecosystems/{ecosystem_id}/characterization-items", response_model=List[ItemCharacterization])
async def get_characterization_items(
    ecosystem_id: str,
    key: str = Query(..., description="Clave de la sub-caracterización"),
    active_only: bool = Query(True, description="Si es True, solo devuelve items activos"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los items de caracterización para un ecosistema y una clave específica.
    
    Args:
        ecosystem_id: ID del ecosistema
        key: Clave de la sub-caracterización (ej: 'objetivos_estrategicos')
        active_only: Si es True, solo devuelve items activos
        
    Returns:
        Lista de items de caracterización activos
    """
    try:
        items_data = CharacterizationService.get_characterization_items_by_key(
            ecosystem_id=ecosystem_id,
            key=key,
            db=db,
            active_only=active_only
        )
        
        # Convertir los resultados a un formato de respuesta
        items = [ItemCharacterization(**item) for item in items_data]
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener items de caracterización: {str(e)}")


@router.get("/ecosystems/{ecosystem_id}/strategic-objectives", response_model=List[ItemCharacterization])
async def get_strategic_objectives(
    ecosystem_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene los objetivos estratégicos para un ecosistema específico.
    
    Args:
        ecosystem_id: ID del ecosistema
        
    Returns:
        Lista de objetivos estratégicos activos
    """
    try:
        items_data = CharacterizationService.get_strategic_objectives(
            ecosystem_id=ecosystem_id,
            db=db
        )
        
        # Convertir los resultados a un formato de respuesta
        items = [ItemCharacterization(**item) for item in items_data]
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener objetivos estratégicos: {str(e)}")


# Función auxiliar para obtener items de caracterización desde el código
def get_characterization_items_by_key(ecosystem_id: str, key: str, db: Session) -> List[Dict[str, Any]]:
    """
    Función auxiliar para obtener items de caracterización para un ecosistema y una clave específica.
    
    Args:
        ecosystem_id: ID del ecosistema
        key: Clave de la sub-caracterización
        db: Sesión de base de datos
        
    Returns:
        Lista de items de caracterización como diccionarios
    """
    return CharacterizationService.get_characterization_items_by_key(
        ecosystem_id=ecosystem_id,
        key=key,
        db=db
    )


# Función auxiliar para obtener objetivos estratégicos desde el código (mantener por compatibilidad)
def get_strategic_objectives_for_ecosystem(ecosystem_id: str, db: Session) -> List[Dict[str, Any]]:
    """
    Función auxiliar para obtener objetivos estratégicos para un ecosistema.
    
    Args:
        ecosystem_id: ID del ecosistema
        db: Sesión de base de datos
        
    Returns:
        Lista de objetivos estratégicos como diccionarios
    """
    return CharacterizationService.get_strategic_objectives(ecosystem_id, db)
