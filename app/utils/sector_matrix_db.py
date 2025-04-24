import os
import pandas as pd
import logging
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db, SessionLocal
from app.db.models import SectorMatrix


class SectorMatrixDB:
    """
    Clase para manejar la matriz sectorial usando SQLite y caché en memoria.
    """
    _instance = None
    _matrix_cache = None
    
    def __new__(cls):
        """Implementación de patrón Singleton para asegurar una sola instancia."""
        if cls._instance is None:
            cls._instance = super(SectorMatrixDB, cls).__new__(cls)
            cls._instance._initialize_db()
        return cls._instance
    
    def _initialize_db(self):
        """Inicializa la conexión a la base de datos PostgreSQL."""
        # La tabla sector_matrix ya está definida en los modelos SQLAlchemy
        # y se crea automáticamente al iniciar la aplicación
        logging.info("Inicializando conexión a la base de datos de matriz sectorial")
        
        # No es necesario crear tablas manualmente, SQLAlchemy se encarga de esto
        # a través de los modelos definidos en app/db/models.py
    
    def import_from_excel(self, excel_path: str) -> None:
        """
        Importa la matriz sectorial desde un archivo Excel a la base de datos.
        
        Args:
            excel_path: Ruta al archivo Excel con la matriz
        """
        # Cargar matriz desde Excel
        matriz = pd.read_excel(excel_path, index_col=0)
        matriz.index = matriz.index.astype(str)
        
        # Normalizar códigos CIIU
        nuevo_index = []
        for idx in matriz.index:
            if len(idx) == 3:
                idx = idx.zfill(4)
            nuevo_index.append(idx)
        
        matriz.index = nuevo_index
        matriz.columns = nuevo_index
        
        # Usar sesión de SQLAlchemy
        db = SessionLocal()
        try:
            # Limpiar tabla existente
            db.query(SectorMatrix).delete()
            
            # Insertar valores
            for codigo1 in matriz.index:
                for codigo2 in matriz.columns:
                    valor = float(matriz.loc[codigo1, codigo2])
                    sector_matrix = SectorMatrix(
                        codigo1=codigo1,
                        codigo2=codigo2,
                        valor=valor
                    )
                    db.add(sector_matrix)
            
            db.commit()
            
            # Limpiar caché
            self._matrix_cache = None
            
            logging.info(f"Matriz sectorial importada a la base de datos desde {excel_path}")
        except Exception as e:
            db.rollback()
            logging.error(f"Error al importar matriz sectorial: {str(e)}")
            raise
        finally:
            db.close()
    
    def get_valor(self, codigo1: str, codigo2: str) -> float:
        """
        Obtiene el valor de compatibilidad entre dos códigos CIIU.
        
        Args:
            codigo1: Primer código CIIU
            codigo2: Segundo código CIIU
            
        Returns:
            Valor de compatibilidad (0 si no existe)
        """
        # Normalizar códigos
        if len(codigo1) == 3:
            codigo1 = codigo1.zfill(4)
        if len(codigo2) == 3:
            codigo2 = codigo2.zfill(4)
        
        # Verificar si tenemos la matriz en caché
        if self._matrix_cache is not None:
            return self._matrix_cache.get(codigo1, {}).get(codigo2, 0.0)
        
        # Si no está en caché, consultar la base de datos
        db = SessionLocal()
        try:
            resultado = db.query(SectorMatrix).filter(
                SectorMatrix.codigo1 == codigo1,
                SectorMatrix.codigo2 == codigo2
            ).first()
            
            return float(resultado.valor) if resultado else 0.0
        finally:
            db.close()
    
    def get_full_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Obtiene la matriz completa como un diccionario anidado.
        La carga en memoria para acceso rápido en futuras consultas.
        
        Returns:
            Diccionario con la matriz de compatibilidad sectorial
        """
        # Si ya está en caché, retornarla
        if self._matrix_cache is not None:
            return self._matrix_cache
        
        # Cargar desde la base de datos
        db = SessionLocal()
        try:
            resultados = db.query(SectorMatrix).all()
            
            # Construir diccionario
            matriz_dict = {}
            for resultado in resultados:
                codigo1 = resultado.codigo1
                codigo2 = resultado.codigo2
                valor = float(resultado.valor)
                
                if codigo1 not in matriz_dict:
                    matriz_dict[codigo1] = {}
                matriz_dict[codigo1][codigo2] = valor
            
            # Guardar en caché
            self._matrix_cache = matriz_dict
            
            return matriz_dict
        finally:
            db.close()
    
    def is_db_initialized(self) -> bool:
        """
        Verifica si la base de datos ya tiene datos.
        
        Returns:
            True si la base de datos ya tiene datos, False en caso contrario
        """
        db = SessionLocal()
        try:
            count = db.query(SectorMatrix).count()
            return count > 0
        finally:
            db.close()


def initialize_sector_matrix(excel_path: Optional[str] = None) -> None:
    """
    Inicializa la matriz sectorial desde un archivo Excel si es necesario.
    
    Args:
        excel_path: Ruta al archivo Excel con la matriz (opcional)
    """
    db = SectorMatrixDB()
    
    # Si la base de datos ya está inicializada, no hacer nada
    if db.is_db_initialized():
        logging.info("Base de datos de matriz sectorial ya inicializada")
        return
    
    # Si no se proporcionó una ruta, buscar el archivo en la ubicación configurada
    if excel_path is None:
        excel_path = get_settings().EXCEL_MATRIZ_PATH
        
        # Si no hay ruta configurada, buscar en la ubicación predeterminada
        if excel_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            excel_path = os.path.join(base_dir, 'matriz.xlsx')
    
    # Verificar si existe el archivo
    if not os.path.exists(excel_path):
        error_msg = f"No se encontró la matriz sectorial en {excel_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logging.info(f"Inicializando matriz sectorial desde: {excel_path}")
    # Importar desde Excel
    db.import_from_excel(excel_path)


def get_sector_matrix() -> Dict[str, Dict[str, float]]:
    """
    Obtiene la matriz sectorial completa.
    
    Returns:
        Diccionario con la matriz de compatibilidad sectorial
    """
    db = SectorMatrixDB()
    return db.get_full_matrix()


def get_sector_compatibility(codigo1: str, codigo2: str) -> float:
    """
    Obtiene el valor de compatibilidad entre dos códigos CIIU.
    
    Args:
        codigo1: Primer código CIIU
        codigo2: Segundo código CIIU
        
    Returns:
        Valor de compatibilidad (0 si no existe)
    """
    db = SectorMatrixDB()
    return db.get_valor(codigo1, codigo2)
