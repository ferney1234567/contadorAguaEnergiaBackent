from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.session import engine, Base
from app.routers import agua, energia, lecturas, metas

app = FastAPI(
    title="Backend Contadores",
    version="1.0.0",
    description="API de consumo de Agua y Energía con OCR"
)

# ✅ Crear tablas cuando la app arranca (más seguro en Render)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# ✅ CORS (lo ajustamos abajo)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agua.router)
app.include_router(energia.router)
app.include_router(lecturas.router)
app.include_router(metas.router)


@app.get("/", tags=["Root"])
def read_root():
    return {"status": "OK", "mensaje": "Backend funcionando", "version": "1.0.0"}