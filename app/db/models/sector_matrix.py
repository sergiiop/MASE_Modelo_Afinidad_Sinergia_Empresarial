from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.db.database import Base

class SectorMatrix(Base):
    """Modelo para la matriz de compatibilidad sectorial."""
    __tablename__ = "sector_matrix"
    __table_args__ = {"schema": "empresa_master"}

    id = Column(Integer, primary_key=True, index=True)
    codigo1 = Column(String(10), nullable=False, index=True)
    codigo2 = Column(String(10), nullable=False, index=True)
    valor = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
