from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.session import Base


class SedeEnergia(Base):
    __tablename__ = "sedes_energia"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(150), nullable=False)
    ubicacion = Column(String(150), nullable=False)
    cuenta = Column(String(50), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )