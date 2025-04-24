from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import logging

from app.db.database import get_db
from app.db.models import Match, MatchExecution, Company
from app.models.schemas import MatchResult

logger = logging.getLogger(__name__)

class MatchExecutionService:
    """Servicio para gestionar las ejecuciones de matching."""
    
    @staticmethod
    def create_match_execution(ecosystem_id: str, description: str = None, db: Session = None) -> MatchExecution:
        """
        Crea un nuevo registro de ejecución de matching.
        
        Args:
            ecosystem_id: ID del ecosistema
            description: Descripción opcional de esta ejecución
            db: Sesión de base de datos (opcional)
            
        Returns:
            Objeto MatchExecution creado
        """
        close_db = False
        if db is None:
            db = next(get_db())
            close_db = True
            
        try:
            match_execution = MatchExecution(
                ecosystem_id=ecosystem_id,
                description=description
            )
            db.add(match_execution)
            db.commit()
            db.refresh(match_execution)
            return match_execution
        finally:
            if close_db:
                db.close()
    
    @staticmethod
    def store_match(match_result: MatchResult, execution_id: str, ecosystem_id: str, db: Session = None) -> Match:
        """
        Almacena un resultado de match asociado a una ejecución.
        
        Args:
            match_result: Resultado del match a almacenar
            execution_id: ID de la ejecución
            ecosystem_id: ID del ecosistema
            db: Sesión de base de datos (opcional)
            
        Returns:
            Objeto Match almacenado
        """
        close_db = False
        if db is None:
            db = next(get_db())
            close_db = True
            
        try:
            # Obtener IDs de empresas a partir de NITs
            company_a = db.query(Company).filter(Company.nit == match_result.nit_1).first()
            company_b = db.query(Company).filter(Company.nit == match_result.nit_2).first()
            
            if not company_a or not company_b:
                raise ValueError(f"No se encontraron las empresas con NITs {match_result.nit_1} y {match_result.nit_2}")
            
            # Verificar si ya existe un match entre estas empresas
            existing_match = db.query(Match).filter(
                or_(
                    and_(Match.empresa_a_id == company_a.id, Match.empresa_b_id == company_b.id),
                    and_(Match.empresa_a_id == company_b.id, Match.empresa_b_id == company_a.id)
                ),
                Match.ecosistema_id == ecosystem_id
            ).first()
            
            if existing_match:
                # Actualizar match existente
                existing_match.match_execution_id = execution_id
                existing_match.affinity = match_result.match_afinidad
                existing_match.synergy = match_result.match_sinergia
                existing_match.employees_match = match_result.diferencia_empleados
                existing_match.city_match = match_result.match_ciudad
                existing_match.size_match = match_result.match_tamaño
                existing_match.sector_match = match_result.match_sector
                existing_match.total_score = match_result.puntaje_total
                existing_match.explanation = {
                    "affinity": match_result.exp_afinidad,
                    "synergy": match_result.exp_sinergia,
                    "employees": match_result.exp_empleados,
                    "city": match_result.exp_ciudad,
                    "size": match_result.exp_tamaño,
                    "sector": match_result.exp_sector
                }
                
                db.commit()
                return existing_match
            else:
                # Crear nuevo match
                new_match = Match(
                    match_execution_id=execution_id,
                    empresa_a_id=company_a.id,
                    empresa_b_id=company_b.id,
                    ecosistema_id=ecosystem_id,
                    affinity=match_result.match_afinidad,
                    synergy=match_result.match_sinergia,
                    employees_match=match_result.diferencia_empleados,
                    city_match=match_result.match_ciudad,
                    size_match=match_result.match_tamaño,
                    sector_match=match_result.match_sector,
                    total_score=match_result.puntaje_total,
                    explanation={
                        "affinity": match_result.exp_afinidad,
                        "synergy": match_result.exp_sinergia,
                        "employees": match_result.exp_empleados,
                        "city": match_result.exp_ciudad,
                        "size": match_result.exp_tamaño,
                        "sector": match_result.exp_sector
                    }
                )
                db.add(new_match)
                db.commit()
                db.refresh(new_match)
                return new_match
        except Exception as e:
            db.rollback()
            logger.error(f"Error al almacenar match: {str(e)}")
            raise
        finally:
            if close_db:
                db.close()
    
    @staticmethod
    def get_execution_matches(execution_id: str, db: Session = None) -> List[Match]:
        """
        Obtiene todos los matches asociados a una ejecución.
        
        Args:
            execution_id: ID de la ejecución
            db: Sesión de base de datos (opcional)
            
        Returns:
            Lista de objetos Match
        """
        close_db = False
        if db is None:
            db = next(get_db())
            close_db = True
            
        try:
            return db.query(Match).filter(Match.match_execution_id == execution_id).all()
        finally:
            if close_db:
                db.close()
    
    @staticmethod
    def get_ecosystem_executions(ecosystem_id: str, limit: int = 10, db: Session = None) -> List[MatchExecution]:
        """
        Obtiene las ejecuciones de matching para un ecosistema.
        
        Args:
            ecosystem_id: ID del ecosistema
            limit: Número máximo de resultados
            db: Sesión de base de datos (opcional)
            
        Returns:
            Lista de objetos MatchExecution
        """
        close_db = False
        if db is None:
            db = next(get_db())
            close_db = True
            
        try:
            return db.query(MatchExecution).filter(
                MatchExecution.ecosistema_id == ecosystem_id
            ).order_by(MatchExecution.execution_date.desc()).limit(limit).all()
        finally:
            if close_db:
                db.close()
