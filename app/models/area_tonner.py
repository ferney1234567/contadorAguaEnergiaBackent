from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.session import Base


class AreaTonner(Base):
    __tablename__ = "areas_tonners"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(150), nullable=False, unique=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),   # 🔥 importante
        onupdate=func.now()
    )