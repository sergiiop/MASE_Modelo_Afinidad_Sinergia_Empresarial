import os
import sys
import pandas as pd
import logging
import argparse
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Agregar el directorio raíz al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.models.sector_matrix import SectorMatrix
from app.core.config import get_settings

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def import_sector_matrix_from_excel(file_path: str, db_url: str) -> None:
    """
    Importa la matriz sectorial desde un archivo Excel a PostgreSQL.
    
    Args:
        file_path: Ruta al archivo Excel con la matriz
        db_url: URL de conexión a la base de datos
    """
    if not os.path.exists(file_path):
        logger.error(f"No se encontró el archivo Excel en {file_path}")
        return
    
    logger.info(f"Importando matriz sectorial desde Excel ({file_path}) a PostgreSQL...")
    
    try:
        # Cargar matriz desde Excel
        logger.info(f"Leyendo archivo Excel: {file_path}")
        try:
            matriz = pd.read_excel(file_path, index_col=0)
            logger.info(f"Dimensiones de la matriz: {matriz.shape}")
            logger.info(f"Primeras filas y columnas: \n{matriz.iloc[:5, :5]}")
            
            if matriz.empty:
                logger.error("La matriz está vacía. Verificar el archivo Excel.")
                return
                
            matriz.index = matriz.index.astype(str)
            logger.info(f"Tipos de datos: {matriz.dtypes}")
            
            # Normalizar códigos CIIU
            nuevo_index = []
            for idx in matriz.index:
                if len(idx) == 3:
                    idx = idx.zfill(4)
                nuevo_index.append(idx)
            
            matriz.index = nuevo_index
            matriz.columns = nuevo_index
            logger.info(f"Matriz normalizada. Dimensiones: {matriz.shape}")
        except Exception as e:
            logger.error(f"Error al leer el archivo Excel: {str(e)}")
            # Intentar leer sin especificar index_col
            logger.info("Intentando leer el archivo sin especificar index_col...")
            matriz = pd.read_excel(file_path)
            logger.info(f"Dimensiones de la matriz: {matriz.shape}")
            logger.info(f"Columnas: {matriz.columns.tolist()}")
            logger.info(f"Primeras filas: \n{matriz.head()}")
        
        # Conectar a la base de datos
        engine = create_engine(db_url)
        
        # Verificar si el esquema empresa_master existe
        inspector = inspect(engine)
        if 'empresa_master' not in inspector.get_schema_names():
            logger.info("Creando esquema empresa_master...")
            with engine.connect() as conn:
                conn.execute("CREATE SCHEMA IF NOT EXISTS empresa_master")
                conn.commit()
        
        # Crear tabla si no existe
        SectorMatrix.__table__.create(bind=engine, checkfirst=True)
        
        # Crear sesión
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Eliminar datos existentes si hay
            try:
                count = session.query(SectorMatrix).delete()
                session.commit()
                logger.info(f"Se eliminaron {count} registros existentes.")
            except Exception as e:
                session.rollback()
                logger.warning(f"No se pudieron eliminar registros existentes: {str(e)}")
            
            # Insertar nuevos datos
            count = 0
            
            # Verificar si la matriz tiene el formato esperado (matriz cuadrada con índices y columnas)
            if hasattr(matriz, 'index') and hasattr(matriz, 'columns') and len(matriz.index) > 0 and len(matriz.columns) > 0:
                logger.info("Procesando matriz en formato cuadrado...")
                for codigo1 in matriz.index:
                    for codigo2 in matriz.columns:
                        try:
                            valor = float(matriz.loc[codigo1, codigo2])
                            sector_matrix = SectorMatrix(
                                codigo1=str(codigo1),
                                codigo2=str(codigo2),
                                valor=valor
                            )
                            session.add(sector_matrix)
                            count += 1
                            
                            # Commit cada 1000 registros para evitar problemas de memoria
                            if count % 1000 == 0:
                                session.commit()
                                logger.info(f"Procesados {count} registros...")
                        except Exception as e:
                            logger.warning(f"Error al procesar valor para {codigo1}, {codigo2}: {str(e)}")
            # Si la matriz no tiene el formato esperado, intentar procesarla como una tabla de tres columnas
            elif len(matriz.columns) >= 3:
                logger.info("Procesando matriz en formato tabular...")
                # Determinar qué columnas usar
                col_names = matriz.columns.tolist()
                logger.info(f"Columnas disponibles: {col_names}")
                
                # Buscar columnas que puedan contener códigos CIIU y valores
                codigo1_col = None
                codigo2_col = None
                valor_col = None
                
                # Buscar por nombres comunes
                for col in col_names:
                    col_lower = str(col).lower()
                    if 'codigo1' in col_lower or 'ciiu1' in col_lower or 'sector1' in col_lower:
                        codigo1_col = col
                    elif 'codigo2' in col_lower or 'ciiu2' in col_lower or 'sector2' in col_lower:
                        codigo2_col = col
                    elif 'valor' in col_lower or 'compatibilidad' in col_lower or 'match' in col_lower:
                        valor_col = col
                
                # Si no se encontraron por nombre, usar las primeras tres columnas
                if codigo1_col is None and len(col_names) > 0:
                    codigo1_col = col_names[0]
                if codigo2_col is None and len(col_names) > 1:
                    codigo2_col = col_names[1]
                if valor_col is None and len(col_names) > 2:
                    valor_col = col_names[2]
                
                logger.info(f"Usando columnas: {codigo1_col}, {codigo2_col}, {valor_col}")
                
                # Procesar cada fila
                for _, row in matriz.iterrows():
                    try:
                        codigo1 = str(row[codigo1_col])
                        codigo2 = str(row[codigo2_col])
                        valor = float(row[valor_col])
                        
                        # Normalizar códigos CIIU
                        if len(codigo1) == 3:
                            codigo1 = codigo1.zfill(4)
                        if len(codigo2) == 3:
                            codigo2 = codigo2.zfill(4)
                        
                        sector_matrix = SectorMatrix(
                            codigo1=codigo1,
                            codigo2=codigo2,
                            valor=valor
                        )
                        session.add(sector_matrix)
                        count += 1
                        
                        # Commit cada 1000 registros para evitar problemas de memoria
                        if count % 1000 == 0:
                            session.commit()
                            logger.info(f"Procesados {count} registros...")
                    except Exception as e:
                        logger.warning(f"Error al procesar fila: {str(e)}")
            else:
                logger.error("No se pudo determinar el formato de la matriz. Verificar el archivo Excel.")
            
            session.commit()
            logger.info(f"Importación completada. Se importaron {count} registros.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error al importar datos: {str(e)}")
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error al leer el archivo Excel: {str(e)}")

def main():
    """Función principal para importar la matriz sectorial."""
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description="Importar matriz sectorial desde Excel a PostgreSQL")
    parser.add_argument("--host", help="Host de PostgreSQL")
    parser.add_argument("--port", help="Puerto de PostgreSQL")
    parser.add_argument("--user", help="Usuario de PostgreSQL")
    parser.add_argument("--password", help="Contraseña de PostgreSQL")
    parser.add_argument("--db", help="Nombre de la base de datos")
    parser.add_argument("--excel", help="Ruta al archivo Excel con la matriz sectorial")
    
    args = parser.parse_args()
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    # Obtener la configuración desde el archivo .env
    settings = get_settings()
    
    # Usar argumentos de línea de comandos si están presentes, de lo contrario usar configuración
    host = args.host or settings.POSTGRES_SERVER
    port = args.port or settings.POSTGRES_PORT
    user = args.user or settings.POSTGRES_USER
    password = args.password or settings.POSTGRES_PASSWORD
    db = args.db or settings.POSTGRES_DB
    
    # Construir URL de conexión a la base de datos
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    logger.info(f"Conectando a la base de datos: {host}:{port}/{db} como usuario {user}")
    
    # Ruta al archivo Excel con la matriz sectorial
    excel_path = args.excel or os.environ.get("MATRIZ_SECTORIAL_PATH") or "./matriz.xlsx"
    
    if not os.path.exists(excel_path):
        logger.error(f"No se encontró el archivo Excel en {excel_path}")
        logger.info("Buscando alternativas...")
        
        # Buscar en el directorio raíz del proyecto
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Intentar encontrar cualquier archivo Excel que pueda contener la matriz
        for file_name in ["matriz.xlsx", "CIIU.xlsx", "data.xlsx", "Emparejamientos.xlsx"]:
            alt_path = os.path.join(root_dir, file_name)
            if os.path.exists(alt_path):
                excel_path = alt_path
                logger.info(f"Se utilizará el archivo alternativo: {excel_path}")
                break
        else:
            logger.error("No se encontró ningún archivo Excel compatible.")
            excel_path = input("Ingrese la ruta al archivo Excel con la matriz sectorial: ")
            if not os.path.exists(excel_path):
                logger.error(f"No se encontró el archivo Excel en {excel_path}")
                return
    
    logger.info(f"Utilizando archivo Excel: {excel_path}")
    
    # Importar matriz sectorial
    import_sector_matrix_from_excel(excel_path, db_url)

if __name__ == "__main__":
    main()
