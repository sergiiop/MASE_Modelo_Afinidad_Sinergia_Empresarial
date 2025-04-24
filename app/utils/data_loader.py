import pandas as pd
from typing import Tuple, Dict, List
from app.models.schemas import Empresa


def load_data_from_excel(file_path: str) -> List[Empresa]:
    """
    Carga datos de empresas desde un archivo Excel.
    
    Args:
        file_path: Ruta al archivo Excel
        
    Returns:
        Lista de objetos Empresa
    """
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
    
    # Normalizar código CIIU
    if "codigo_ciiu" in df.columns:
        df["codigo_ciiu"] = df["codigo_ciiu"].astype(str)
        df["codigo_ciiu"] = df["codigo_ciiu"].apply(
            lambda x: x.zfill(4) if len(x) == 3 else x
        )
    
    # Convertir DataFrame a lista de objetos Empresa
    empresas = []
    for _, row in df.iterrows():
        empresa_dict = row.to_dict()
        empresas.append(Empresa(**empresa_dict))
    
    return empresas


def load_sector_matrix(file_path: str) -> Dict[str, Dict[str, float]]:
    """
    Carga la matriz de compatibilidad sectorial desde un archivo Excel.
    
    Args:
        file_path: Ruta al archivo Excel
        
    Returns:
        Diccionario con la matriz de compatibilidad sectorial
    """
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
    
    # Convertir a diccionario
    matriz_dict = {}
    for idx in matriz.index:
        matriz_dict[idx] = {}
        for col in matriz.columns:
            matriz_dict[idx][col] = float(matriz.loc[idx, col])
    
    return matriz_dict
