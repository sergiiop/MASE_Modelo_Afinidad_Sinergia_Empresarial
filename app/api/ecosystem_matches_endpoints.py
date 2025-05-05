from fastapi import APIRouter, Depends, Query, HTTPException, Path, Body
from sqlalchemy.orm import Session, joinedload
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.models.schemas import MatchResponse, MatchResult, Empresa
from app.services.matching_service import MatchingService
from app.services.match_storage_service import MatchStorageService
from app.services.match_execution_service import MatchExecutionService
from app.services.characterization_service import CharacterizationService
from app.db.models import Company, Match, EcosystemCompany

router = APIRouter()
logger = logging.getLogger(__name__)

def clean_ciiu_code(code: str) -> str:
    """Limpia el código CIIU removiendo la letra inicial si existe."""
    if not code:
        return None
    # Si el código comienza con una letra, la removemos
    if code and code[0].isalpha():
        return code[1:]
    return code


class CompanyMatchRequest(BaseModel):
    """Modelo para la solicitud de generación de matches."""
    company_ids: List[str]
    description: Optional[str] = None

@router.post("/ecosystems/{ecosystem_id}/generate-matches", response_model=Dict[str, Any])
async def generate_ecosystem_matches(
    ecosystem_id: str,
    request: CompanyMatchRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Genera matches para las empresas especificadas en un ecosistema y los asocia a una ejecución.
    
    Args:
        ecosystem_id: ID del ecosistema
        request: Objeto con los IDs de las empresas y una descripción opcional
        
    Returns:
        Mensaje de confirmación con el número de matches generados
    """
    try:
        logger.info(f"Iniciando generación de matches para el ecosistema {ecosystem_id} con {len(request.company_ids)} empresas seleccionadas")
        
        # Obtener solo las empresas especificadas en el request que pertenecen al ecosistema
        # Incluir las relaciones necesarias (ciudad y ciiu)
        companies = db.query(Company).options(
            joinedload(Company.ciudad),
            joinedload(Company.ciiu),
            joinedload(Company.company_size)
        ).join(
            EcosystemCompany, 
            EcosystemCompany.empresa_id == Company.id
        ).filter(
            EcosystemCompany.ecosistema_id == ecosystem_id,
            Company.id.in_(request.company_ids)
        ).all()
        
        logger.info(f"Se encontraron {len(companies)} empresas en el ecosistema")

        if not companies:
            raise HTTPException(status_code=404, detail=f"No hay empresas en el ecosistema {ecosystem_id}")
            
        # Convertir las empresas al formato esperado por el servicio de matching
        empresas = []
        for company in companies:
            # Obtener valores de las relaciones
            ciudad_nombre = company.ciudad.nombre if company.ciudad else None
            codigo_ciiu = clean_ciiu_code(company.ciiu.codigo) if company.ciiu else None
            descripcion_ciiu = company.ciiu.descripcion if company.ciiu else None
            size = company.company_size.descripcion if company.company_size else None
            
            # Obtener datos estratégicos de la relación EcosystemCompany
            ecosystem_company = db.query(EcosystemCompany).filter(
                EcosystemCompany.ecosistema_id == ecosystem_id,
                EcosystemCompany.empresa_id == company.id
            ).first()
            
            additional_data = ecosystem_company.additional_data if ecosystem_company and ecosystem_company.additional_data else {}
            
            strategic_objectives = CharacterizationService.get_strategic_objectives(
                ecosystem_id=ecosystem_id,
                db=db
            )

            interests = CharacterizationService.get_interests(
                ecosystem_id=ecosystem_id,
                db=db
            )
            
            # Si hay datos adicionales y objetivos estratégicos, actualizar los valores
            if additional_data and 'intereses' in additional_data:
                char_data = additional_data.get('intereses', {})
                
                for obj in interests:
                    obj_key = obj.get('key')
                    if obj_key in char_data:
                        # Convertir a 1 si está marcado como verdadero
                        interests_values[obj_key] = 1 if char_data.get(obj_key) else 0

            if additional_data and 'objetivos_estrategicos' in additional_data:
                char_data = additional_data.get('objetivos_estrategicos', {})
                for obj in strategic_objectives:
                    obj_key = obj.get('key')
                    if obj_key in char_data:
                        # Convertir a 1 si está marcado como verdadero
                        strategic_values[obj_key] = 1 if char_data.get(obj_key) else 0
            
            empresa = Empresa(
                nit=company.nit,
                razonsocial=company.razonsocial,
                nombrecomercial=company.nombrecomercial,
                codigo_ciiu=codigo_ciiu,
                descripcion_ciiu=descripcion_ciiu,
                ciudad=ciudad_nombre,
                size=size,
                num_empleados_directos=company.num_empleados_directos,
                num_empleados_indirectos=company.num_empleados_indirectos,
                **strategic_values,
                **interests_values
            )
            empresas.append(empresa)
        
        # Crear un nuevo registro de ejecución
        logger.info("Creando registro de ejecución de matches")
        match_execution = MatchExecutionService.create_match_execution(ecosystem_id, request.description, db)
        logger.info(f"Registro de ejecución creado con ID: {match_execution.id}")
        
        # Generar matches
        matching_service = MatchingService()
        match_results = matching_service.generar_matching_mase(
            empresas=empresas,
            batch_size=200  # Tamaño de lote optimizado para procesamiento paralelo
        )
        
        # Almacenar los matches usando inserción masiva
        logger.info(f"Iniciando almacenamiento masivo de {len(match_results)} matches")
        stored_matches = MatchExecutionService.store_matches_bulk(
            match_results=match_results,
            execution_id=match_execution.id,
            ecosystem_id=ecosystem_id,
            db=db,
            batch_size=1000  # Insertar en lotes de 1000
        )
        logger.info(f"Almacenamiento masivo completado. Total de matches: {stored_matches}")
        
        logger.info(f"Proceso completado. Total de matches almacenados: {stored_matches}")
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
