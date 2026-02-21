import os
from pathlib import Path
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==================================================
# CARGAR .env DESDE LA RAÍZ DEL PROYECTO
# ==================================================
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD") or ""
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

print("DB CONFIG →", DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

if not all([DB_USER, DB_HOST, DB_NAME]):
    raise RuntimeError("❌ Variables del .env no cargadas correctamente")

# ==================================================
# CADENA DE CONEXIÓN MYSQL (LOCAL)
# ==================================================
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

# ==================================================
# ENGINE
# ==================================================
engine = create_engine(
    DATABASE_URL,
    echo=True,          # 🔍 logs SQL en local
    pool_pre_ping=True
)

# ==================================================
# SESSION FACTORY
# ==================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==================================================
# BASE PARA MODELOS
# ==================================================
Base = declarative_base()

# ==================================================
# DEPENDENCIA FASTAPI
# ==================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
