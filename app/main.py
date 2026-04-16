from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.database.session import engine, Base
from app.routers import agua, energia, inspeccion_sanitario, lecturas, metas, comparativoAgua, comparativoEnergia, inspeccion_residuos,areas, inspeccion_energia, areas_sanitaria, areas_resmas,resmas, sedes,tonners,areas_tonners,sedesEnergia,areas_energia


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
app.include_router(comparativoEnergia.router)
app.include_router(comparativoAgua.router)
app.include_router(inspeccion_residuos.router)
app.include_router(areas.router)
app.include_router(inspeccion_energia.router)
app.include_router(inspeccion_sanitario.router)
app.include_router(areas_sanitaria.router)
app.include_router(areas_resmas.router)
app.include_router(resmas.router)
app.include_router(sedes.router)
app.include_router(tonners.router)
app.include_router(areas_tonners.router)
app.include_router(sedesEnergia.router)
app.include_router(areas_energia.router)



@app.get("/", tags=["Root"])
def read_root():
    return {"status": "OK", "mensaje": "Backend funcionando", "version": "1.0.0"}