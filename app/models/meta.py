from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from app.database.session import Base

class Meta(Base):
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)   # "agua" | "energia"
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    meta = Column(Float, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
