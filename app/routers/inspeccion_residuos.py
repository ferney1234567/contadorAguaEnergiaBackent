from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.session import get_db
from app.models.inspeccion_residuos import InspeccionResiduos
from app.models.area import Area  # 🔥 IMPORTANTE

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
# ✅ CREAR INSPECCIÓN
# ======================================================
@router.post("/")
def crear_inspeccion(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    fecha = data.get("fecha")
    responsable = data.get("responsable")
    area_id = data.get("area_id")  # 🔥 CAMBIO

    if not all([fecha, responsable, area_id]):
        raise HTTPException(
            status_code=400,
            detail="Faltan datos obligatorios"
        )

    # 🔥 VALIDAR QUE EL AREA EXISTE
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(
            status_code=404,
            detail="El área no existe"
        )

    total = calcular_total(data)

    nueva = InspeccionResiduos(
        fecha=fecha,
        responsable=responsable,
        area_id=area_id,  # 🔥 CAMBIO

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
        "mensaje": "Inspección creada correctamente",
        "id": nueva.id,
        "total": nueva.total
    }


# ======================================================
# 📄 LISTAR INSPECCIONES
# ======================================================
@router.get("/")
def listar_inspecciones(db: Session = Depends(get_db)):
    registros = (
        db.query(InspeccionResiduos)
        .order_by(InspeccionResiduos.fecha.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "fecha": r.fecha,
            "responsable": r.responsable,
            "area_id": r.area_id,
            "area": r.area.nombre if r.area else None,  # 🔥 CLAVE

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
# 🔍 OBTENER UNA
# ======================================================
@router.get("/{id}")
def obtener_inspeccion(id: int, db: Session = Depends(get_db)):
    r = db.query(InspeccionResiduos).filter(InspeccionResiduos.id == id).first()

    if not r:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")

    return {
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


# ======================================================
# ❌ ELIMINAR
# ======================================================
@router.delete("/{id}")
def eliminar_inspeccion(id: int, db: Session = Depends(get_db)):
    registro = db.query(InspeccionResiduos).filter(
        InspeccionResiduos.id == id
    ).first()

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="No existe la inspección"
        )

    db.delete(registro)
    db.commit()

    return {
        "mensaje": "Inspección eliminada correctamente",
        "id": id
    }