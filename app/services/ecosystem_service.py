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
    
    def _initialize_db(self):
        """Inicializa la base de datos PostgreSQL para ecosistemas."""
        db = next(get_db())
        db.execute('''
        CREATE TABLE IF NOT EXISTS ecosystems (
            id UUID PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            company_id UUID,
            peso_afinidad REAL NOT NULL,
            peso_sinergia REAL NOT NULL,
            peso_empleados REAL NOT NULL,
            peso_ciudad REAL NOT NULL,
            peso_tamaño REAL NOT NULL,
            peso_sector REAL NOT NULL,
            max_matches_per_company INTEGER NOT NULL,
            min_match_score REAL NOT NULL,
            active BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        db.commit()
        logging.info("Base de datos de ecosistemas inicializada")
    
    def create_ecosystem(self, ecosystem: EcosystemConfig) -> EcosystemConfig:
        """Crea un nuevo ecosistema en la base de datos."""
        db = next(get_db())
        try:
            # Verificar si ya existe un ecosistema con el mismo ID (si se proporciona)
            if ecosystem.id and db.query(Ecosystem).filter(Ecosystem.id == ecosystem.id).first():
                raise ValueError(f"Ya existe un ecosistema con el ID {ecosystem.id}")
            
            # Crear un nuevo objeto Ecosystem para la base de datos
            new_ecosystem = Ecosystem(
                id=ecosystem.id or uuid.uuid4(),
                name=ecosystem.name,
                description=ecosystem.description,
                company_id=ecosystem.company_id,
                peso_afinidad=ecosystem.peso_afinidad,
                peso_sinergia=ecosystem.peso_sinergia,
                peso_empleados=ecosystem.peso_empleados,
                peso_ciudad=ecosystem.peso_ciudad,
                peso_tamaño=ecosystem.peso_tamaño,
                peso_sector=ecosystem.peso_sector,
                max_matches_per_company=ecosystem.max_matches_per_company,
                min_match_score=ecosystem.min_match_score,
                active=ecosystem.active
            )
            
            # Insertar en la base de datos
            db.add(new_ecosystem)
            db.commit()
            db.refresh(new_ecosystem)
            
            # Actualizar caché
            self._ecosystems_cache[new_ecosystem.id] = ecosystem
            
            # Actualizar el ID en el objeto devuelto
            ecosystem.id = new_ecosystem.id
            
            return ecosystem
        except Exception as e:
            db.rollback()
            raise
    
    def update_ecosystem(self, ecosystem: EcosystemConfig) -> EcosystemConfig:
        """Actualiza un ecosistema existente."""
        db = next(get_db())
        try:
            # Verificar si existe el ecosistema
            ecosystem_db = db.query(Ecosystem).filter(Ecosystem.id == ecosystem.id).first()
            if not ecosystem_db:
                raise ValueError(f"No existe un ecosistema con el ID {ecosystem.id}")
            
            # Actualizar los campos
            ecosystem_db.name = ecosystem.name
            ecosystem_db.description = ecosystem.description
            ecosystem_db.company_id = ecosystem.company_id
            ecosystem_db.peso_afinidad = ecosystem.peso_afinidad
            ecosystem_db.peso_sinergia = ecosystem.peso_sinergia
            ecosystem_db.peso_empleados = ecosystem.peso_empleados
            ecosystem_db.peso_ciudad = ecosystem.peso_ciudad
            ecosystem_db.peso_tamaño = ecosystem.peso_tamaño
            ecosystem_db.peso_sector = ecosystem.peso_sector
            ecosystem_db.max_matches_per_company = ecosystem.max_matches_per_company
            ecosystem_db.min_match_score = ecosystem.min_match_score
            ecosystem_db.active = ecosystem.active
            
            # Guardar cambios
            db.commit()
            db.refresh(ecosystem_db)
            
            # Actualizar caché
            self._ecosystems_cache[ecosystem.id] = ecosystem
            
            return ecosystem
        except Exception as e:
            db.rollback()
            raise
    
    def get_ecosystem(self, ecosystem_id: str) -> Optional[EcosystemConfig]:
        """Obtiene un ecosistema por su ID."""
        # Verificar si está en caché
        if ecosystem_id in self._ecosystems_cache:
            return self._ecosystems_cache[ecosystem_id]
        
        # Buscar en la base de datos
        db = next(get_db())
        ecosystem_db = db.query(Ecosystem).filter(Ecosystem.id == ecosystem_id).first()
        
        if not ecosystem_db:
            return None
        
        # Crear objeto EcosystemConfig
        # Preparar los datos para el modelo Pydantic
        ecosystem_data = {
            "id": ecosystem_db.id,
            "name": ecosystem_db.name,
            "description": ecosystem_db.description,
            "peso_afinidad": ecosystem_db.peso_afinidad,
            "peso_sinergia": ecosystem_db.peso_sinergia,
            "peso_empleados": ecosystem_db.peso_empleados,
            "peso_ciudad": ecosystem_db.peso_ciudad,
            "peso_tamaño": ecosystem_db.peso_tamaño,
            "peso_sector": ecosystem_db.peso_sector,
            "max_matches_per_company": ecosystem_db.max_matches_per_company,
            "min_match_score": ecosystem_db.min_match_score,
            "active": ecosystem_db.active
        }
        
        # Añadir company_id solo si no es None
        if ecosystem_db.company_id is not None:
            ecosystem_data["company_id"] = ecosystem_db.company_id
            
        ecosystem = EcosystemConfig(**ecosystem_data)
        
        # Actualizar caché
        self._ecosystems_cache[ecosystem_id] = ecosystem
        
        return ecosystem
    
    def delete_ecosystem(self, ecosystem_id: str) -> bool:
        """Elimina un ecosistema por su ID."""
        db = next(get_db())
        try:
            # Verificar si existe el ecosistema
            ecosystem_db = db.query(Ecosystem).filter(Ecosystem.id == ecosystem_id).first()
            if not ecosystem_db:
                return False
            
            # Eliminar de la base de datos
            db.delete(ecosystem_db)
            db.commit()
            
            # Eliminar de caché
            if ecosystem_id in self._ecosystems_cache:
                del self._ecosystems_cache[ecosystem_id]
            
            return True
        except Exception as e:
            db.rollback()
            raise
    
    def list_ecosystems(self) -> List[EcosystemConfig]:
        """Lista todos los ecosistemas disponibles."""
        db = next(get_db())
        ecosystems_db = db.query(Ecosystem).all()
        
        ecosystems = []
        for eco_db in ecosystems_db:
            # Preparar los datos para el modelo Pydantic
            ecosystem_data = {
                "id": eco_db.id,
                "name": eco_db.name,
                "description": eco_db.description,
                "peso_afinidad": eco_db.peso_afinidad,
                "peso_sinergia": eco_db.peso_sinergia,
                "peso_empleados": eco_db.peso_empleados,
                "peso_ciudad": eco_db.peso_ciudad,
                "peso_tamaño": eco_db.peso_tamaño,
                "peso_sector": eco_db.peso_sector,
                "max_matches_per_company": eco_db.max_matches_per_company,
                "min_match_score": eco_db.min_match_score,
                "active": eco_db.active
            }
            
            # Añadir company_id solo si no es None
            if eco_db.company_id is not None:
                ecosystem_data["company_id"] = eco_db.company_id
                
            ecosystem = EcosystemConfig(**ecosystem_data)
            
            ecosystems.append(ecosystem)
            self._ecosystems_cache[eco_db.id] = ecosystem
        
        return ecosystems
    
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
