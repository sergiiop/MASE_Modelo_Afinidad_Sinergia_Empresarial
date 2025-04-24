from typing import Dict, Optional
import pandas as pd
import os
import logging
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db.models import SectorMatrix

logger = logging.getLogger(__name__)

class SectorMatrixService:
    """Servicio para manejar la matriz sectorial desde la base de datos."""
    
    @classmethod
    def get_compatibility(cls, codigo1: str, codigo2: str, db: Session) -> float:
        """
        Obtiene la compatibilidad entre dos códigos CIIU desde la base de datos.
        
        Args:
            codigo1: Primer código CIIU
            codigo2: Segundo código CIIU
            db: Sesión de base de datos
            
        Returns:
            Valor de compatibilidad entre 0 y 1
        """
        
        # Normalizar códigos
        if len(codigo1) == 3:
            codigo1 = codigo1.zfill(4)
        if len(codigo2) == 3:
            codigo2 = codigo2.zfill(4)
        
        # Buscar en la base de datos (considerando ambas direcciones)
        compatibility = db.query(SectorMatrix).filter(
            or_(
                and_(SectorMatrix.codigo1 == codigo1, SectorMatrix.codigo2 == codigo2),
                and_(SectorMatrix.codigo1 == codigo2, SectorMatrix.codigo2 == codigo1)
            )
        ).first()
        
        if not compatibility:
            logger.warning(f"No se encontró compatibilidad en la base de datos para los códigos CIIU: {codigo1}, {codigo2}")
            return 0.0
        
        return compatibility.valor
