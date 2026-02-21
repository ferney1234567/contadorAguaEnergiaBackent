from sqlalchemy import Column, Integer, Float, Date, DateTime
from sqlalchemy.sql import func
from app.database.session import Base


class ConsumoAgua(Base):
    __tablename__ = "consumo_agua"

    id = Column(Integer, primary_key=True, index=True)

    # Fecha real del consumo
    fecha = Column(Date, nullable=False, index=True)

    # Lecturas de contadores
    bodega1 = Column(Integer, nullable=False)
    bodega2 = Column(Integer, nullable=False)

    # Consumo diario calculado
    total_bodega1 = Column(Float, nullable=False)
    total_bodega2 = Column(Float, nullable=False)

    # Total del día
    sumatoria = Column(Float, nullable=False)

    # Auditoría
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
