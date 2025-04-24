import logging
import os
import pandas as pd
from sqlalchemy.orm import Session

from app.db.database import Base, engine, get_db
from app.core.config import get_settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SectorMatrix:
    """Clase para manejar la matriz sectorial."""
    
    @staticmethod
    def import_from_excel(file_path: str) -> None:
        """
        Importa la matriz sectorial desde un archivo Excel.
        
        Args:
            file_path: Ruta al archivo Excel con la matriz
        """
        if not os.path.exists(file_path):
            logger.error(f"No se encontró el archivo Excel en {file_path}")
            return
        
        logger.info(f"Importando matriz sectorial desde Excel ({file_path})...")
        
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
            matriz_dict = {}
            for codigo1 in matriz.index:
                matriz_dict[codigo1] = {}
                for codigo2 in matriz.columns:
                    matriz_dict[codigo1][codigo2] = float(matriz.loc[codigo1, codigo2])
            
            return matriz_dict
        except Exception as e:
            logger.error(f"Error al leer el archivo Excel: {str(e)}")
            return None


def init_db() -> None:
    """Inicializa la base de datos creando todas las tablas necesarias."""
    logger.info("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas correctamente.")


def main() -> None:
    """Función principal para inicializar la base de datos."""
    logger.info("Inicializando base de datos...")
    
    # Crear tablas
    init_db()
    
    # Cargar matriz sectorial si se especifica
    settings = get_settings()
    excel_path = os.environ.get("MATRIZ_SECTORIAL_PATH") or "./data/matriz_sectorial.xlsx"
    if os.path.exists(excel_path):
        matriz = SectorMatrix.import_from_excel(excel_path)
        if matriz:
            logger.info(f"Matriz sectorial cargada correctamente con {len(matriz)} códigos CIIU.")
    
    logger.info("Inicialización de base de datos completada.")


if __name__ == "__main__":
    main()
