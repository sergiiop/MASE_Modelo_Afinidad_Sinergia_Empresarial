from fastapi import APIRouter, Depends, Query, HTTPException, Path
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.schemas import MatchResponse, MatchResult, Empresa
from app.services.matching_service import MatchingService
from app.services.match_storage_service import MatchStorageService
from app.services.match_execution_service import MatchExecutionService
from app.db.models import Company, Match

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ecosystems/{ecosystem_id}/generate-matches", response_model=Dict[str, Any])
async def generate_ecosystem_matches(
    ecosystem_id: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Genera matches para todas las empresas en un ecosistema y los asocia a una ejecución.
    
    Args:
        ecosystem_id: ID del ecosistema
        description: Descripción opcional para esta ejecución
        
    Returns:
        Mensaje de confirmación con el número de matches generados
    """
    try:
        # Obtener todas las empresas del ecosistema desde la base de datos principal
        companies = MatchStorageService.get_ecosystem_companies(ecosystem_id, db)
        if not companies:
            raise HTTPException(status_code=404, detail=f"No hay empresas en el ecosistema {ecosystem_id}")
        
        # Convertir las empresas al formato esperado por el servicio de matching
        empresas = []
        for company in companies:
            empresa = Empresa(
                nit=company.nit,
                razonsocial=company.razonsocial,
                nombrecomercial=company.nombrecomercial,
                codigo_ciiu=company.codigo_ciiu,
                descripcion_ciiu=company.descripcion_ciiu,
                ciudad=company.ciudad,
                tamaño=company.tamaño,
                num_empleados_directos=company.num_empleados_directos,
                num_empleados_indirectos=company.num_empleados_indirectos,
                crear_nuevos_modelos_negocio=company.crear_nuevos_modelos_negocio,
                generar_eficiencias=company.generar_eficiencias,
                fidelizar_mercado_actual=company.fidelizar_mercado_actual,
                diversificar_mercado=company.diversificar_mercado,
                incremento_ventas=company.incremento_ventas,
                llegar_nuevos_mercados=company.llegar_nuevos_mercados,
                lanzamiento_nuevos_productos=company.lanzamiento_nuevos_productos,
                mejoramiento_productividad=company.mejoramiento_productividad,
                incremento_capacidad_productiva=company.incremento_capacidad_productiva,
                desarrollo_nuevos_canales=company.desarrollo_nuevos_canales,
                implementacion_ti=company.implementacion_ti,
                infraestructura_fisica=company.infraestructura_fisica,
                compra_maquinaria_equipos=company.compra_maquinaria_equipos
            )
            empresas.append(empresa)
        
        # Crear un nuevo registro de ejecución
        match_execution = MatchExecutionService.create_match_execution(ecosystem_id, description, db)
        
        # Generar matches
        matching_service = MatchingService()
        match_results = matching_service.generar_matching_mase(
            empresas=empresas,
            ecosystem_id=ecosystem_id,
            limit=10,  # Valor predeterminado
            min_score=0.0  # Valor predeterminado
        )
        
        # Almacenar los matches asociados a esta ejecución
        stored_matches = 0
        for match_result in match_results:
            MatchExecutionService.store_match(match_result, match_execution.id, ecosystem_id, db)
            stored_matches += 1
        
        return {
            "message": f"Se generaron {stored_matches} matches para el ecosistema {ecosystem_id}",
            "execution_id": match_execution.id,
            "total_matches": stored_matches
        }
    except Exception as e:
        logger.error(f"Error al generar matches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al generar matches: {str(e)}")

@router.get("/companies/{nit}/matches", response_model=List[MatchResult])
async def get_company_matches(
    nit: str = Path(..., description="NIT de la empresa"),
    ecosystem_id: str = Query(..., description="ID del ecosistema"),
    limit: Optional[int] = Query(10, description="Número máximo de matches a retornar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los matches de una empresa específica.
    
    Este endpoint es para uso de cada empresa. Devuelve los matches almacenados
    para una empresa específica, ordenados por puntaje total.
    
    Args:
        nit: NIT de la empresa
        ecosystem_id: ID del ecosistema
        limit: Número máximo de matches a retornar
        
    Returns:
        Lista de objetos MatchResult con los matches de la empresa
    """
    try:
        # Obtener la empresa por NIT
        company = db.query(Company).filter(Company.nit == nit).first()
        if not company:
            raise HTTPException(status_code=404, detail=f"Empresa con NIT {nit} no encontrada")
        
        # Obtener los matches de la empresa usando el servicio
        matches = MatchStorageService.get_company_matches(company.id, ecosystem_id, limit, db)
        
        return matches
    except Exception as e:
        logger.error(f"Error al obtener matches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener matches: {str(e)}")
