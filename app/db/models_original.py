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
    ecosystem_id = Column(String(36), ForeignKey("empresa_master.ecosistema.id"), nullable=False)
    description = Column(String(255), nullable=True)
    execution_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    matches = relationship("Match", back_populates="execution")


class Match(Base):
    """Modelo para almacenar matches entre empresas."""
    __tablename__ = "match_ecosistema"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Referencia a la ejecución
    match_execution_id = Column(String(36), 
        ForeignKey("empresa_master.match_execution.id", 
            name="fk_match_ecosistema_execution"), 
        nullable=False)
    execution = relationship("MatchExecution", back_populates="matches")
    
    # Empresas involucradas
    empresa_a_id = Column(String(36), 
        ForeignKey("empresa_master.companies.id", 
            name="fk_match_ecosistema_empresa_a"), 
        nullable=False)
    companyA = relationship("Company", foreign_keys=[empresa_a_id])
    
    empresa_b_id = Column(String(36), 
        ForeignKey("empresa_master.companies.id", 
            name="fk_match_ecosistema_empresa_b"), 
        nullable=False)
    companyB = relationship("Company", foreign_keys=[empresa_b_id])
    
    ecosistema_id = Column(String(36), 
        ForeignKey("empresa_master.ecosistema.id", 
            name="fk_match_ecosistema_ecosistema"), 
        nullable=False)
    ecosystem = relationship("Ecosistema", back_populates="matches")
    
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
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Modelo mínimo para empresas (solo para referencias)
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey, func
from sqlalchemy.orm import relationship

class Ciudad(Base):
    __tablename__ = "ciudad"
    __table_args__ = {"schema": "public", "extend_existing": True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(300), nullable=False)
    codigo = Column(String(5), unique=True, nullable=True)
    lat = Column(Float, unique=True, nullable=True)
    long = Column(Float, unique=True, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    empresas = relationship('Company', back_populates='ciudad', primaryjoin='public.ciudad.c.id == empresa_master.companies.c.ciudad_id')

class CiiuEntity(Base):
    __tablename__ = "ciiu"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(String(36), primary_key=True)
    codigo = Column(String(6), nullable=False)
    descripcion = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    empresas = relationship('Company', back_populates='ciiu')

class Ecosistema(Base):
    """Modelo para ecosistemas de empresas."""
    __tablename__ = "ecosistema"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relaciones
    companies = relationship('Company', secondary='empresa_master.ecosystem_company', back_populates='ecosistemas')
    matches = relationship('Match', back_populates='ecosystem')


class EcosystemCompany(Base):
    """Modelo para la relación muchos a muchos entre ecosistemas y empresas."""
    __tablename__ = "ecosystem_company"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ecosistema_id = Column(String(36), ForeignKey('empresa_master.ecosistema.id'), nullable=False)
    empresa_id = Column(String(36), ForeignKey('empresa_master.companies.id'), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Company(Base):
    """Modelo de empresas actualizado según versión NestJS."""
    __tablename__ = "companies"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    nit = Column(String(60), unique=True, nullable=True)
    razonsocial = Column(String(255), nullable=True)
    nombrecomercial = Column(String(255), nullable=True)
    num_empleados_directos = Column(Integer, nullable=True, default=0)
    num_empleados_indirectos = Column(Integer, nullable=True, default=0)
    
    # Campos de estrategia
    crear_nuevos_modelos_negocio = Column(Boolean, nullable=True, default=False)
    generar_eficiencias = Column(Boolean, nullable=True, default=False)
    fidelizar_mercado_actual = Column(Boolean, nullable=True, default=False)
    diversificar_mercado = Column(Boolean, nullable=True, default=False)
    incremento_ventas = Column(Boolean, nullable=True, default=False)
    llegar_nuevos_mercados = Column(Boolean, nullable=True, default=False)
    lanzamiento_nuevos_productos = Column(Boolean, nullable=True, default=False)
    mejoramiento_productividad = Column(Boolean, nullable=True, default=False)
    incremento_capacidad_productiva = Column(Boolean, nullable=True, default=False)
    desarrollo_nuevos_canales = Column(Boolean, nullable=True, default=False)
    implementacion_ti = Column(Boolean, nullable=True, default=False)
    infraestructura_fisica = Column(Boolean, nullable=True, default=False)
    compra_maquinaria_equipos = Column(Boolean, nullable=True, default=False)
    
    # Campos adicionales
    size_company = Column(String(255), nullable=True)
    
    # Relationships
    ciudad_id = Column(Integer, ForeignKey('public.ciudad.id', ondelete='SET NULL'), nullable=True)
    ciudad = relationship('Ciudad', back_populates='empresas')
    
    actividad_economica_id = Column(String(36), ForeignKey('empresa_master.ciiu.id'), nullable=True)
    ciiu = relationship('CiiuEntity', back_populates='empresas')
    
    # Relación con ecosistemas
    ecosistemas = relationship('Ecosistema', secondary='empresa_master.ecosystem_company', back_populates='companies')


class SectorMatrix(Base):
    """Modelo para la matriz de compatibilidad entre sectores CIIU."""
    __tablename__ = "sector_matrix"
    __table_args__ = {'schema': 'public', 'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo1 = Column(String(10), nullable=False, index=True)
    codigo2 = Column(String(10), nullable=False, index=True)
    valor = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
