from typing import Dict, Optional
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class SectorMatrixService:
    """Servicio para manejar la matriz sectorial en memoria."""
    
    _matriz: Dict[str, Dict[str, float]] = {}
    _is_loaded = False
    
    @classmethod
    def load_matrix(cls, file_path: str) -> bool:
        """
        Carga la matriz sectorial desde un archivo Excel.
        
        Args:
            file_path: Ruta al archivo Excel con la matriz
            
        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        if not os.path.exists(file_path):
            logger.error(f"No se encontró el archivo Excel en {file_path}")
            return False
        
        logger.info(f"Cargando matriz sectorial desde Excel ({file_path})...")
        
        try:
            # Cargar matriz desde Excel
            matriz = pd.read_excel(file_path, index_col=0)
            matriz.index = matriz.index.astype(str)
            
            # Normalizar códigos CIIU
            nuevo_index = []
            for idx in matriz.index:
                if len(idx) == 3:
                    idx = idx.zfill(4)
                nuevo_index.append(idx)
            
            matriz.index = nuevo_index
            matriz.columns = nuevo_index
            
            # Convertir a diccionario para uso en memoria
            cls._matriz = {}
            for codigo1 in matriz.index:
                cls._matriz[codigo1] = {}
                for codigo2 in matriz.columns:
                    cls._matriz[codigo1][codigo2] = float(matriz.loc[codigo1, codigo2])
            
            cls._is_loaded = True
            logger.info(f"Matriz sectorial cargada correctamente con {len(cls._matriz)} códigos CIIU.")
            return True
        except Exception as e:
            logger.error(f"Error al leer el archivo Excel: {str(e)}")
            return False
    
    @classmethod
    def get_compatibility(cls, codigo1: str, codigo2: str) -> float:
        """
        Obtiene la compatibilidad entre dos códigos CIIU.
        
        Args:
            codigo1: Primer código CIIU
            codigo2: Segundo código CIIU
            
        Returns:
            Valor de compatibilidad entre 0 y 1
        """
        if not cls._is_loaded:
            logger.warning("La matriz sectorial no ha sido cargada.")
            return 0.0
        
        # Normalizar códigos
        if len(codigo1) == 3:
            codigo1 = codigo1.zfill(4)
        if len(codigo2) == 3:
            codigo2 = codigo2.zfill(4)
        
        # Verificar si los códigos existen en la matriz
        if codigo1 not in cls._matriz or codigo2 not in cls._matriz:
            logger.warning(f"Uno o ambos códigos CIIU no existen en la matriz: {codigo1}, {codigo2}")
            return 0.0
        
        # Obtener compatibilidad
        return cls._matriz[codigo1][codigo2]
