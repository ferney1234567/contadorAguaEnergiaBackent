from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class ComparativoAgua(Base):
    __tablename__ = "comparativo_agua"

    id = Column(Integer, primary_key=True, index=True)

    # 🔥 RELACIÓN CON SEDE
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)

    sede = relationship("Sede")

    # Fecha del consumo
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)

    # Consumo de agua
    m3_consumidos = Column(Float, nullable=True)

    # Valor pagado
    valor_consumo_agua = Column(Float, nullable=True)

    # Indicador de cumplimiento
    cumple = Column(Boolean, default=True)

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