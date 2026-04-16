from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.inspeccion_energia import InspeccionEnergia
from app.models.AreaEnergia import AreaEnergia
from sqlalchemy import func
from datetime import datetime

router = APIRouter(
    prefix="/inspecciones-energia",
    tags=["Inspecciones Energia"]
)

# ======================================================
# 🧠 CALCULAR TOTAL
# ======================================================
def calcular_total(data):
    return (
        (data.get("bombillas_c") or 0) +
        (data.get("bombillas_nc") or 0) +
        (data.get("reflectores_c") or 0) +
        (data.get("reflectores_nc") or 0) +
        (data.get("lamparas_c") or 0) +
        (data.get("lamparas_nc") or 0) +
        (data.get("aires_c") or 0) +
        (data.get("aires_nc") or 0)
    )

# ======================================================
# 🧠 CALCULAR SEMANA
# ======================================================
def obtener_semana(fecha):
    d = datetime.fromisoformat(str(fecha))
    inicio = datetime(d.year, 1, 1)
    dias = (d - inicio).days
    return int((dias + inicio.weekday() + 1) / 7) + 1

# ======================================================
# 🔥 UPSERT (SEMANAL)
# ======================================================
@router.post("/")
def upsert_inspeccion(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    fecha = data.get("fecha")
    responsable = data.get("responsable")
    area_id = data.get("area_id")

    if not all([fecha, responsable, area_id]):
        raise HTTPException(400, "Faltan datos obligatorios")

    # 🔥 VALIDAR AREA ENERGIA
    area = db.query(AreaEnergia).filter(AreaEnergia.id == area_id).first()
    if not area:
        raise HTTPException(404, "El área de energía no existe")

    # 🔥 CALCULAR AÑO Y SEMANA
    fecha_dt = datetime.fromisoformat(str(fecha))
    anio = fecha_dt.year
    semana = obtener_semana(fecha)

    total = calcular_total(data)

    # 🔥 BUSCAR POR SEMANA (NO POR FECHA)
    registro = db.query(InspeccionEnergia).filter(
        InspeccionEnergia.anio == anio,
        InspeccionEnergia.semana == semana,
        InspeccionEnergia.responsable == responsable,
        InspeccionEnergia.area_id == area_id
    ).first()

    # ================= UPDATE =================
    if registro:
        registro.bombillas_c = data.get("bombillas_c", 0)
        registro.bombillas_nc = data.get("bombillas_nc", 0)

        registro.reflectores_c = data.get("reflectores_c", 0)
        registro.reflectores_nc = data.get("reflectores_nc", 0)

        registro.lamparas_c = data.get("lamparas_c", 0)
        registro.lamparas_nc = data.get("lamparas_nc", 0)

        registro.aires_c = data.get("aires_c", 0)
        registro.aires_nc = data.get("aires_nc", 0)

        registro.observacion = data.get("observacion")
        registro.total = total

        db.commit()
        db.refresh(registro)

        return {
            "mensaje": "Actualizado correctamente",
            "id": registro.id,
            "total": registro.total
        }

    # ================= CREATE =================
    nueva = InspeccionEnergia(
        fecha=fecha_dt,
        responsable=responsable,
        area_id=area_id,

        bombillas_c=data.get("bombillas_c", 0),
        bombillas_nc=data.get("bombillas_nc", 0),

        reflectores_c=data.get("reflectores_c", 0),
        reflectores_nc=data.get("reflectores_nc", 0),

        lamparas_c=data.get("lamparas_c", 0),
        lamparas_nc=data.get("lamparas_nc", 0),

        aires_c=data.get("aires_c", 0),
        aires_nc=data.get("aires_nc", 0),

        observacion=data.get("observacion"),
        total=total,

        anio=anio,
        semana=semana
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {
        "mensaje": "Creado correctamente",
        "id": nueva.id,
        "total": nueva.total
    }

# ======================================================
# 📄 LISTAR
# ======================================================
@router.get("/")
def listar_inspecciones(db: Session = Depends(get_db)):
    registros = db.query(InspeccionEnergia).all()

    return [
        {
            "id": r.id,
            "fecha": r.fecha,
            "responsable": r.responsable,
            "area_id": r.area_id,
            "area": r.area.nombre if r.area else None,

            "anio": r.anio,
            "semana": r.semana,

            "bombillas_c": r.bombillas_c,
            "bombillas_nc": r.bombillas_nc,

            "reflectores_c": r.reflectores_c,
            "reflectores_nc": r.reflectores_nc,

            "lamparas_c": r.lamparas_c,
            "lamparas_nc": r.lamparas_nc,

            "aires_c": r.aires_c,
            "aires_nc": r.aires_nc,

            "observacion": r.observacion,
            "total": r.total
        }
        for r in registros
    ]

# ======================================================
# ❌ DELETE POR SEMANA
# ======================================================
@router.delete("/")
def eliminar_inspeccion_energia(data: dict = Body(...), db: Session = Depends(get_db)):
    responsable = data.get("responsable")
    fecha = data.get("fecha")

    if not responsable or not fecha:
        raise HTTPException(400, "Faltan datos")

    fecha_dt = datetime.fromisoformat(str(fecha))
    anio = fecha_dt.year
    semana = obtener_semana(fecha)

    registros = db.query(InspeccionEnergia).filter(
        InspeccionEnergia.responsable == responsable,
        InspeccionEnergia.anio == anio,
        InspeccionEnergia.semana == semana
    ).all()

    if not registros:
        raise HTTPException(404, "No se encontraron registros")

    for r in registros:
        db.delete(r)

    db.commit()

    return {"mensaje": "Inspección semanal eliminada correctamente"}