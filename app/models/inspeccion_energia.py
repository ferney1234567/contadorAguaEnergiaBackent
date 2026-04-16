from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class InspeccionEnergia(Base):
    __tablename__ = "inspecciones_energia"

    id = Column(Integer, primary_key=True, index=True)

    # 📅 Datos principales
    fecha = Column(DateTime, nullable=False)
    responsable = Column(String(150), nullable=False)

    # 🔥 RELACIÓN CORRECTA (CAMBIO CLAVE)
    area_id = Column(Integer, ForeignKey("areas_energia.id"), nullable=False)
    area = relationship("AreaEnergia")

    # ⚡ CAMPOS DE ENERGÍA

    # Bombillas
    bombillas_c = Column(Integer, default=0)
    bombillas_nc = Column(Integer, default=0)

    # Reflectores
    reflectores_c = Column(Integer, default=0)
    reflectores_nc = Column(Integer, default=0)

    # Lámparas
    lamparas_c = Column(Integer, default=0)
    lamparas_nc = Column(Integer, default=0)

    # Aires acondicionados
    aires_c = Column(Integer, default=0)
    aires_nc = Column(Integer, default=0)

    # 📝 Observaciones
    observacion = Column(String(500), nullable=True)

    # 🔢 Total
    total = Column(Integer, default=0)

    # 🔥 SEMANAL (CLAVE PARA TU SISTEMA)
    anio = Column(Integer, nullable=False)
    semana = Column(Integer, nullable=False)

    # 🕒 Auditoría
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )