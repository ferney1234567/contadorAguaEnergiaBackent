from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base


class ComparativoEnergia(Base):
    __tablename__ = "comparativo_energia"

    id = Column(Integer, primary_key=True, index=True)

    # 🔗 RELACIÓN CON SEDE (CORREGIDO)
    sede_energia = Column(
        Integer,
        ForeignKey("sedes_energia.id", ondelete="CASCADE"),
        nullable=False
    )

    # 📅 FECHA
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)

    # ⚡ CONSUMO
    kw_consumidos = Column(Float, nullable=True, default=0)

    # 💰 VALOR
    valor_consumo_energia = Column(Float, nullable=True, default=0)

    # ✔ CUMPLE
    cumple = Column(Boolean, default=True)

    # 🕒 AUDITORÍA
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # 🔥 RELACIÓN ORM (CORREGIDO)
    sede = relationship("SedeEnergia")

    # 🚨 CLAVE ÚNICA (CORREGIDA)
    __table_args__ = (
        UniqueConstraint("sede_energia", "anio", "mes", name="unique_energia"),
    )