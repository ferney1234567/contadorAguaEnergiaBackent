from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func

from app.database.session import get_db
from app.models.inspeccion_residuos import InspeccionResiduos
from app.models.area import Area

router = APIRouter(
    prefix="/inspecciones-residuos",
    tags=["Inspecciones Residuos"]
)

# ======================================================
# 🧠 CALCULAR TOTAL
# ======================================================
def calcular_total(data):
    return (
        (data.get("reciclables_c") or 0) +
        (data.get("ordinarios_c") or 0) +
        (data.get("peligrosos_c") or 0) +
        (data.get("presintos_c") or 0)
    )

# ======================================================
# 🔥 UPSERT (CREAR O ACTUALIZAR AUTOMÁTICO)
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

    # 🔥 VALIDAR ÁREA
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(404, "El área no existe")

    # ======================================================
    # 🔥 BUSCAR SI YA EXISTE (CLAVE REAL DEL SISTEMA)
    # ======================================================
    registro = db.query(InspeccionResiduos).filter(
        InspeccionResiduos.fecha == fecha,
        InspeccionResiduos.responsable == responsable,
        InspeccionResiduos.area_id == area_id
    ).first()

    total = calcular_total(data)

    # ======================================================
    # ✏️ UPDATE
    # ======================================================
    if registro:
        registro.reciclables_c = data.get("reciclables_c", 0)
        registro.reciclables_nc = data.get("reciclables_nc", 0)

        registro.ordinarios_c = data.get("ordinarios_c", 0)
        registro.ordinarios_nc = data.get("ordinarios_nc", 0)

        registro.peligrosos_c = data.get("peligrosos_c", 0)
        registro.peligrosos_nc = data.get("peligrosos_nc", 0)

        registro.presintos_c = data.get("presintos_c", 0)
        registro.presintos_nc = data.get("presintos_nc", 0)

        registro.observacion = data.get("observacion")
        registro.total = total

        db.commit()
        db.refresh(registro)

        return {
            "mensaje": "Actualizado correctamente",
            "id": registro.id,
            "total": registro.total
        }

    # ======================================================
    # ➕ CREATE
    # ======================================================
    nueva = InspeccionResiduos(
        fecha=fecha,
        responsable=responsable,
        area_id=area_id,

        reciclables_c=data.get("reciclables_c", 0),
        reciclables_nc=data.get("reciclables_nc", 0),

        ordinarios_c=data.get("ordinarios_c", 0),
        ordinarios_nc=data.get("ordinarios_nc", 0),

        peligrosos_c=data.get("peligrosos_c", 0),
        peligrosos_nc=data.get("peligrosos_nc", 0),

        presintos_c=data.get("presintos_c", 0),
        presintos_nc=data.get("presintos_nc", 0),

        observacion=data.get("observacion"),
        total=total
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
    registros = db.query(InspeccionResiduos).all()

    return [
        {
            "id": r.id,
            "fecha": r.fecha,
            "responsable": r.responsable,
            "area_id": r.area_id,
            "area": r.area.nombre if r.area else None,

            "reciclables_c": r.reciclables_c,
            "reciclables_nc": r.reciclables_nc,

            "ordinarios_c": r.ordinarios_c,
            "ordinarios_nc": r.ordinarios_nc,

            "peligrosos_c": r.peligrosos_c,
            "peligrosos_nc": r.peligrosos_nc,

            "presintos_c": r.presintos_c,
            "presintos_nc": r.presintos_nc,

            "observacion": r.observacion,
            "total": r.total
        }
        for r in registros
    ]

# ======================================================
# ❌ DELETE
# ======================================================
@router.delete("/")
def eliminar_inspeccion(data: dict = Body(...), db: Session = Depends(get_db)):
    responsable = data.get("responsable")
    fecha = data.get("fecha")

    if not responsable or not fecha:
        raise HTTPException(400, "Faltan datos")

    registros = db.query(InspeccionResiduos).filter(
        InspeccionResiduos.responsable == responsable,
        func.date(InspeccionResiduos.fecha) == fecha
    ).all()

    for r in registros:
        db.delete(r)

    db.commit()

    return {"mensaje": "Eliminado correctamente"}