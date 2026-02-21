import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==================================================
# CARGAR .env LOCAL (solo si existe)
# ==================================================
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

# ==================================================
# PRIORIDAD 1 → DATABASE_URL (Producción Render)
# PRIORIDAD 2 → Variables separadas (Local)
# ==================================================
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD") or ""
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT") or "5432"
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_HOST, DB_NAME]):
        raise RuntimeError("❌ Variables del .env no cargadas correctamente")

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

# ==================================================
# ENGINE
# ==================================================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# ==================================================
# SESSION
# ==================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()