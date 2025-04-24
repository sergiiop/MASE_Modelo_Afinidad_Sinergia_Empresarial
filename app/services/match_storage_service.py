import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.database import get_db
from app.db.models import Match, Company
from app.models.schemas import MatchResult

logger = logging.getLogger(__name__)

class MatchStorageService:
    """Servicio para obtener matches de la base de datos."""
    
    @staticmethod
    def get_company_matches(company_id: str, ecosystem_id: str, limit: int = 10, db: Session = None) -> List[MatchResult]:
        """
        Obtiene los matches de una empresa específica.
        
        Args:
            company_id: ID de la empresa
            ecosystem_id: ID del ecosistema
            limit: Número máximo de matches a retornar
            db: Sesión de base de datos (opcional)
            
        Returns:
            Lista de objetos MatchResult con los matches de la empresa
        """
        close_db = False
        if db is None:
            db = next(get_db())
            close_db = True
            
        try:
            # Obtener los matches donde la empresa es la primera o la segunda
            matches_db = db.query(Match).filter(
                or_(
                    Match.empresa_a_id == company_id,
                    Match.empresa_b_id == company_id
                ),
                Match.ecosistema_id == ecosystem_id,
                Match.is_active == True
            ).order_by(Match.total_score.desc()).limit(limit).all()
            
            # Convertir a formato de respuesta
            results = []
            for match_db in matches_db:
                # Obtener la otra empresa del match
                if match_db.empresa_a_id == company_id:
                    other_company_id = match_db.empresa_b_id
                    is_first = True
                else:
                    other_company_id = match_db.empresa_a_id
                    is_first = False
                
                # Obtener datos de las empresas
                company = db.query(Company).filter(Company.id == company_id).first()
                other_company = db.query(Company).filter(Company.id == other_company_id).first()
                
                if not company or not other_company:
                    continue
                
                # Crear objeto MatchResult
                if is_first:
                    match_result = MatchResult(
                        nit_1=company.nit,
                        razon_social_1=company.razonsocial,
                        empresa_1=company.nombrecomercial,
                        ciiu_1=company.codigo_ciiu,
                        descripcion_ciiu_1=company.descripcion_ciiu or "",
                        ciudad_1=company.ciudad,
                        tamaño_1=company.tamaño,
                        total_empleados_1=company.num_empleados_directos + company.num_empleados_indirectos,
                        
                        nit_2=other_company.nit,
                        razon_social_2=other_company.razonsocial,
                        empresa_2=other_company.nombrecomercial,
                        ciiu_2=other_company.codigo_ciiu,
                        descripcion_ciiu_2=other_company.descripcion_ciiu or "",
                        ciudad_2=other_company.ciudad,
                        tamaño_2=other_company.tamaño,
                        total_empleados_2=other_company.num_empleados_directos + other_company.num_empleados_indirectos,
                        
                        match_afinidad=match_db.affinity,
                        match_sinergia=match_db.synergy,
                        match_ciudad=match_db.city_match,
                        match_tamaño=match_db.size_match,
                        match_sector=match_db.sector_match,
                        puntaje_total=match_db.total_score,
                        diferencia_empleados=match_db.employees_match,
                        
                        exp_afinidad=match_db.explanation.get("affinity", ""),
                        exp_sinergia=match_db.explanation.get("synergy", ""),
                        exp_empleados=match_db.explanation.get("employees", ""),
                        exp_ciudad=match_db.explanation.get("city", ""),
                        exp_tamaño=match_db.explanation.get("size", ""),
                        exp_sector=match_db.explanation.get("sector", "")
                    )
                else:
                    match_result = MatchResult(
                        nit_1=other_company.nit,
                        razon_social_1=other_company.razonsocial,
                        empresa_1=other_company.nombrecomercial,
                        ciiu_1=other_company.codigo_ciiu,
                        descripcion_ciiu_1=other_company.descripcion_ciiu or "",
                        ciudad_1=other_company.ciudad,
                        tamaño_1=other_company.tamaño,
                        total_empleados_1=other_company.num_empleados_directos + other_company.num_empleados_indirectos,
                        
                        nit_2=company.nit,
                        razon_social_2=company.razonsocial,
                        empresa_2=company.nombrecomercial,
                        ciiu_2=company.codigo_ciiu,
                        descripcion_ciiu_2=company.descripcion_ciiu or "",
                        ciudad_2=company.ciudad,
                        tamaño_2=company.tamaño,
                        total_empleados_2=company.num_empleados_directos + company.num_empleados_indirectos,
                        
                        match_afinidad=match_db.affinity,
                        match_sinergia=match_db.synergy,
                        match_ciudad=match_db.city_match,
                        match_tamaño=match_db.size_match,
                        match_sector=match_db.sector_match,
                        puntaje_total=match_db.total_score,
                        diferencia_empleados=match_db.employees_match,
                        
                        exp_afinidad=match_db.explanation.get("affinity", ""),
                        exp_sinergia=match_db.explanation.get("synergy", ""),
                        exp_empleados=match_db.explanation.get("employees", ""),
                        exp_ciudad=match_db.explanation.get("city", ""),
                        exp_tamaño=match_db.explanation.get("size", ""),
                        exp_sector=match_db.explanation.get("sector", "")
                    )
                
                results.append(match_result)
            
            return results
        except Exception as e:
            logger.error(f"Error al obtener matches: {str(e)}")
            raise
        finally:
            if close_db:
                db.close()
    
    @staticmethod
    def get_ecosystem_companies(ecosystem_id: str, db: Session = None) -> List[Company]:
        """
        Obtiene todas las empresas de un ecosistema.
        
        Args:
            ecosystem_id: ID del ecosistema
            db: Sesión de base de datos (opcional)
            
        Returns:
            Lista de empresas en el ecosistema
        """
        close_db = False
        if db is None:
            db = next(get_db())
            close_db = True
            
        try:
            # Consulta para obtener empresas del ecosistema desde la base de datos principal
            # Nota: Esta consulta debe adaptarse a la estructura real de la base de datos
            return db.query(Company).filter(Company.ecosystem_id == ecosystem_id).all()
        finally:
            if close_db:
                db.close()
