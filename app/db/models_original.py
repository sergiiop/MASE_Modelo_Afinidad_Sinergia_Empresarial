from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class MatchExecution(Base):
    """Registro de una ejecución completa del algoritmo de matching."""
    __tablename__ = "match_execution"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    ecosistema_id = Column(String(36), ForeignKey("empresa_master.ecosistema.id"), nullable=False)
    description = Column(String(255), nullable=True)
    execution_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    matches = relationship("Match", back_populates="execution")


class Match(Base):
    """Modelo para almacenar matches entre empresas."""
    __tablename__ = "match_ecosistema"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Referencia a la ejecución
    execution_id = Column(String(36), ForeignKey("empresa_master.match_execution.id"), nullable=True)
    execution = relationship("MatchExecution", back_populates="matches")
    
    # Empresas involucradas
    empresa_a_id = Column(String(36), ForeignKey("empresa_master.empresa.id"), nullable=False)
    empresa_b_id = Column(String(36), ForeignKey("empresa_master.empresa.id"), nullable=False)
    ecosistema_id = Column(String(36), ForeignKey("empresa_master.ecosistema.id"), nullable=False)
    
    # Resultados del match
    affinity = Column(Integer, nullable=False, default=0)
    synergy = Column(Integer, nullable=False, default=0)
    employees_match = Column(Float, nullable=False, default=0.0)
    city_match = Column(Integer, nullable=False, default=0)
    size_match = Column(Integer, nullable=False, default=0)
    sector_match = Column(Float, nullable=False, default=0.0)
    total_score = Column(Float, nullable=False, default=0.0)
    
    # Explicaciones
    explanation = Column(JSON, nullable=True)
    
    # Estado
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Modelo mínimo para empresas (solo para referencias)
class Company(Base):
    """Modelo mínimo para empresas (solo para referencias)."""
    __tablename__ = "empresa"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(String(36), primary_key=True, index=True)
    nit = Column(String(20), unique=True, index=True, nullable=False)
    razonsocial = Column(String(200), nullable=False)
    nombrecomercial = Column(String(200), nullable=False)
    codigo_ciiu = Column(String(10), nullable=False, index=True)
    descripcion_ciiu = Column(Text, nullable=True)
    ciudad = Column(String(100), nullable=False)
    tamaño = Column(String(50), nullable=False)
    num_empleados_directos = Column(Integer, nullable=False, default=0)
    num_empleados_indirectos = Column(Integer, nullable=False, default=0)
    
    # Campos mínimos de estrategia necesarios para el matching
    crear_nuevos_modelos_negocio = Column(Boolean, nullable=False, default=False)
    generar_eficiencias = Column(Boolean, nullable=False, default=False)
    fidelizar_mercado_actual = Column(Boolean, nullable=False, default=False)
    diversificar_mercado = Column(Boolean, nullable=False, default=False)
    incremento_ventas = Column(Boolean, nullable=False, default=False)
    llegar_nuevos_mercados = Column(Boolean, nullable=False, default=False)
    lanzamiento_nuevos_productos = Column(Boolean, nullable=False, default=False)
    mejoramiento_productividad = Column(Boolean, nullable=False, default=False)
    incremento_capacidad_productiva = Column(Boolean, nullable=False, default=False)
    desarrollo_nuevos_canales = Column(Boolean, nullable=False, default=False)
    implementacion_ti = Column(Boolean, nullable=False, default=False)
    infraestructura_fisica = Column(Boolean, nullable=False, default=False)
    compra_maquinaria_equipos = Column(Boolean, nullable=False, default=False)
