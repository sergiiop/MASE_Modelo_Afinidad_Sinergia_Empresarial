from typing import Dict, List, Optional
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SectorMatrixService:
    """Servicio para manejar la matriz de compatibilidad entre sectores."""
    
    _matrix = None  # Cache de la matriz en memoria
    _matrix_dict = None  # Cache del diccionario en memoria
    
    @classmethod
    def load_matrix(cls) -> tuple[pd.DataFrame, Dict]:
        """
        Carga la matriz de compatibilidad desde el archivo Excel.
        
        Returns:
            Tupla con (DataFrame de la matriz, Diccionario de la matriz)
        """
        if cls._matrix is not None and cls._matrix_dict is not None:
            return cls._matrix, cls._matrix_dict
            
        # Ruta al archivo Excel relativa al directorio del proyecto
        excel_path = Path(__file__).parent.parent.parent / "matriz.xlsx"
        
        # Cargar la matriz desde Excel
        matriz = pd.read_excel(excel_path, index_col=0)
        matriz.index = matriz.index.astype(str)
        
        # Normalizar códigos
        nuevo_index = []
        for idx in matriz.index:
            if len(idx) == 3:
                idx = idx.zfill(4)
            nuevo_index.append(idx)
        matriz.index = nuevo_index
        
        # Convertir a diccionario
        matriz_dict = matriz.to_dict()
        
        cls._matrix = matriz
        cls._matrix_dict = matriz_dict
        logger.info(f"Matriz de compatibilidad cargada desde Excel con {len(matriz.index)} sectores")
        return matriz, matriz_dict
    
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
        # Asegurar que la matriz esté cargada
        _, matrix_dict = cls.load_matrix()
        
        # Normalizar códigos
        if len(codigo1) == 3:
            codigo1 = codigo1.zfill(4)
        if len(codigo2) == 3:
            codigo2 = codigo2.zfill(4)
        
        # Buscar en el diccionario
        if codigo1 in matrix_dict and codigo2 in matrix_dict[codigo1]:
            return matrix_dict[codigo1][codigo2]
            
        logger.warning(f"No se encontró compatibilidad para los códigos CIIU: {codigo1}, {codigo2}")
        return 0.0
