from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base


class InspeccionResiduos(Base):
    __tablename__ = "inspecciones_residuos"

    id = Column(Integer, primary_key=True, index=True)

    # Datos principales
    fecha = Column(DateTime, nullable=False)
    responsable = Column(String(150), nullable=False)

    # 🔥 AQUÍ VA EL CAMBIO IMPORTANTE
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    area = relationship("Area")

    # Reciclables
    reciclables_c = Column(Integer, default=0)
    reciclables_nc = Column(Integer, default=0)

    # Ordinarios
    ordinarios_c = Column(Integer, default=0)
    ordinarios_nc = Column(Integer, default=0)

    # Peligrosos
    peligrosos_c = Column(Integer, default=0)
    peligrosos_nc = Column(Integer, default=0)

    # Presintos
    presintos_c = Column(Integer, default=0)
    presintos_nc = Column(Integer, default=0)

    # Observaciones
    observacion = Column(String(500), nullable=True)

    # Total
    total = Column(Integer, default=0)

    # Auditoría
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )