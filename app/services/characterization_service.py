from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional


class CharacterizationService:
    """Servicio para gestionar las caracterizaciones de empresas."""
    
    @staticmethod
    def get_characterization_items_by_key(
        ecosystem_id: str, 
        key: str, 
        db: Session,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene los items de caracterización para un ecosistema y una clave específica.
        
        Args:
            ecosystem_id: ID del ecosistema
            key: Clave de la sub-caracterización (ej: 'objetivos_estrategicos')
            db: Sesión de base de datos
            active_only: Si es True, solo devuelve items activos
            
        Returns:
            Lista de items de caracterización como diccionarios
        """
        # Construir la consulta SQL
        query_str = """
            SELECT ic.*
            FROM empresa_master.item_characterization ic
            JOIN empresa_master.sub_characterization sc ON ic.sub_characterization_id = sc.id
            JOIN empresa_master.configure_characterization cc ON sc.configure_characterization_id = cc.id
            WHERE cc.ecosistema_id = :ecosystem_id
            AND sc.key = :key
        """
        
        # Añadir filtro de estado si se requiere
        if active_only:
            query_str += " AND ic.estado = true"
            
        query_str += " ORDER BY ic.orden"
        
        # Crear objeto de consulta
        query = text(query_str)
        
        # Ejecutar la consulta
        result = db.execute(query, {"ecosystem_id": ecosystem_id, "key": key})
        
        # Convertir los resultados a una lista de diccionarios
        items = []
        for row in result:
            item_dict = {column: value for column, value in zip(result.keys(), row)}
            items.append(item_dict)
        
        return items
    
    @staticmethod
    def get_strategic_objectives(ecosystem_id: str, db: Session) -> List[Dict[str, Any]]:
        """
        Obtiene los objetivos estratégicos para un ecosistema.
        Método de conveniencia que llama a get_characterization_items_by_key con la clave 'objetivos_estrategicos'.
        
        Args:
            ecosystem_id: ID del ecosistema
            db: Sesión de base de datos
            
        Returns:
            Lista de objetivos estratégicos como diccionarios
        """
        return CharacterizationService.get_characterization_items_by_key(
            ecosystem_id=ecosystem_id,
            key="objetivos_estrategicos",
            db=db
        )

    @staticmethod
    def get_interests(ecosystem_id: str, db: Session) -> List[Dict[str, Any]]:
        """
        Obtiene los intereses para un ecosistema.
        Método de conveniencia que llama a get_characterization_items_by_key con la clave 'intereses'.
        
        Args:
            ecosystem_id: ID del ecosistema
            db: Sesión de base de datos
            
        Returns:
            Lista de intereses como diccionarios
        """
        return CharacterizationService.get_characterization_items_by_key(
            ecosystem_id=ecosystem_id,
            key="intereses",
            db=db
        )
    
    @staticmethod
    def get_sub_characterization(ecosystem_id: str, key: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Obtiene información sobre una sub-caracterización específica.
        
        Args:
            ecosystem_id: ID del ecosistema
            key: Clave de la sub-caracterización
            db: Sesión de base de datos
            
        Returns:
            Diccionario con la información de la sub-caracterización o None si no existe
        """
        query = text("""
            SELECT sc.*
            FROM empresa_master.sub_characterization sc
            JOIN empresa_master.configure_characterization cc ON sc.configure_characterization_id = cc.id
            WHERE cc.ecosistema_id = :ecosystem_id
            AND sc.key = :key
            LIMIT 1
        """)
        
        result = db.execute(query, {"ecosystem_id": ecosystem_id, "key": key})
        row = result.fetchone()
        
        if not row:
            return None
            
        return {column: value for column, value in zip(result.keys(), row)}
