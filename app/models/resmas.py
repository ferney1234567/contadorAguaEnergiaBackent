from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class Resmas(Base):
    __tablename__ = "resmas"

    id = Column(Integer, primary_key=True, index=True)

    area_id = Column(Integer, ForeignKey("areas_resmas.id"), nullable=False)
    area = relationship("AreaResmas")

    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)

    cantidad = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )