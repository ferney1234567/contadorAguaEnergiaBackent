from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.session import Base


class Tonner(Base):
    __tablename__ = "tonners"

    id = Column(Integer, primary_key=True, index=True)

    # 🔗 RELACIÓN CON ÁREA
    area_id = Column(Integer, ForeignKey("areas_tonners.id", ondelete="CASCADE"), nullable=False)

    # 👤 RESPONSABLE
    responsable = Column(String(150), nullable=False)

    # 🖨️ DATOS DEL TONNER      # Ej: HP 85A
    modelo_tonner = Column(String(100), nullable=False)       # Ej: CE285A
    modelo_impresora = Column(String(150), nullable=False)    # Ej: HP LaserJet P1102

    # 📦 CANTIDAD
    cantidad = Column(Integer, nullable=False, default=1)

    # 📅 FECHA
    fecha = Column(DateTime(timezone=True), nullable=False)

    # 🧾 AUDITORÍA
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )