from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Empresa(BaseModel):
    nit: str
    razonsocial: str
    nombrecomercial: str
    codigo_ciiu: str
    descripcion_ciiu: Optional[str] = None
    ciudad: str
    tamaño: str
    num_empleados_directos: int
    num_empleados_indirectos: int
    
    # Campos de estrategia (objetivos)
    crear_nuevos_modelos_negocio: int = Field(ge=0, le=1)
    generar_eficiencias: int = Field(ge=0, le=1)
    fidelizar_mercado_actual: int = Field(ge=0, le=1)
    diversificar_mercado: int = Field(ge=0, le=1)
    
    # Campos de estrategia (intereses)
    incremento_ventas: int = Field(ge=0, le=1)
    llegar_nuevos_mercados: int = Field(ge=0, le=1)
    lanzamiento_nuevos_productos: int = Field(ge=0, le=1)
    mejoramiento_productividad: int = Field(ge=0, le=1)
    incremento_capacidad_productiva: int = Field(ge=0, le=1)
    desarrollo_nuevos_canales: int = Field(ge=0, le=1)
    implementacion_ti: int = Field(ge=0, le=1)
    infraestructura_fisica: int = Field(ge=0, le=1)
    compra_maquinaria_equipos: int = Field(ge=0, le=1)


class EmpresasInput(BaseModel):
    empresas: List[Empresa]
    matriz_sector: Optional[Dict[str, Dict[str, float]]] = None


class MatchConfig(BaseModel):
    peso_afinidad: float = 1.0
    peso_sinergia: float = 1.0
    peso_empleados: float = 1.0
    peso_ciudad: float = 1.0
    peso_tamaño: float = 1.0
    peso_sector: float = 1.0


class MatchRequest(BaseModel):
    empresas: List[Empresa]
    matriz_sector: Optional[Dict[str, Dict[str, float]]] = None
    config: Optional[MatchConfig] = None


class MatchResult(BaseModel):
    nit_1: str
    razon_social_1: str
    empresa_1: str
    ciiu_1: str
    descripcion_ciiu_1: Optional[str] = None
    nit_2: str
    razon_social_2: str
    empresa_2: str
    ciiu_2: str
    descripcion_ciiu_2: Optional[str] = None
    ciudad_1: str
    ciudad_2: str
    tamaño_1: str
    tamaño_2: str
    match_afinidad: int
    match_sinergia: int
    total_empleados_1: int
    total_empleados_2: int
    diferencia_empleados: int
    match_ciudad: int
    match_tamaño: int
    match_sector: float
    puntaje_total: float
    exp_afinidad: str
    exp_sinergia: str
    exp_empleados: str
    exp_ciudad: str
    exp_tamaño: str
    exp_sector: str


class MatchResponse(BaseModel):
    matches: List[MatchResult]
