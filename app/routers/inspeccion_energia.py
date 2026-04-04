from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.session import get_db
from app.models.inspeccion_energia import InspeccionEnergia  # 🔥 CAMBIO
from app.models.area import Area

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
# ✅ CREAR INSPECCIÓN
# ======================================================
@router.post("/")
def crear_inspeccion(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    fecha = data.get("fecha")
    responsable = data.get("responsable")
    area_id = data.get("area_id")

    if not all([fecha, responsable, area_id]):
        raise HTTPException(
            status_code=400,
            detail="Faltan datos obligatorios"
        )

    # 🔥 VALIDAR AREA
    area = db.query(Area).filter(Area.id == area_id).first()

    if not area:
        raise HTTPException(
            status_code=404,
            detail="El área no existe"
        )

    total = calcular_total(data)

    nueva = InspeccionEnergia(
        fecha=fecha,
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
        total=total
    )

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {
        "mensaje": "Inspección de energía creada correctamente",
        "id": nueva.id,
        "total": nueva.total
    }


# ======================================================
# 📄 LISTAR
# ======================================================
@router.get("/")
def listar_inspecciones(db: Session = Depends(get_db)):
    registros = (
        db.query(InspeccionEnergia)
        .order_by(InspeccionEnergia.fecha.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "fecha": r.fecha,
            "responsable": r.responsable,
            "area_id": r.area_id,
            "area": r.area.nombre if r.area else None,

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
# 🔍 OBTENER UNO
# ======================================================
@router.get("/{id}")
def obtener_inspeccion(id: int, db: Session = Depends(get_db)):
    r = db.query(InspeccionEnergia).filter(
        InspeccionEnergia.id == id
    ).first()

    if not r:
        raise HTTPException(
            status_code=404,
            detail="Inspección no encontrada"
        )

    return {
        "id": r.id,
        "fecha": r.fecha,
        "responsable": r.responsable,
        "area_id": r.area_id,
        "area": r.area.nombre if r.area else None,

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

    # ======================================================
# ✏️ ACTUALIZAR INSPECCIÓN ENERGÍA (FORMA CORRECTA)
# ======================================================
@router.put("/{id}")
def actualizar_inspeccion(
    id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    registro = db.query(InspeccionEnergia).filter(
        InspeccionEnergia.id == id
    ).first()

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="No existe la inspección"
        )

    # 🔥 ACTUALIZAR CAMPOS UNO A UNO (MEJOR QUE setattr)
    registro.fecha = data.get("fecha", registro.fecha)
    registro.responsable = data.get("responsable", registro.responsable)
    registro.area_id = data.get("area_id", registro.area_id)

    registro.bombillas_c = int(data.get("bombillas_c") or 0)
    registro.bombillas_nc = int(data.get("bombillas_nc") or 0)

    registro.reflectores_c = int(data.get("reflectores_c") or 0)
    registro.reflectores_nc = int(data.get("reflectores_nc") or 0)

    registro.lamparas_c = int(data.get("lamparas_c") or 0)
    registro.lamparas_nc = int(data.get("lamparas_nc") or 0)

    registro.aires_c = int(data.get("aires_c") or 0)
    registro.aires_nc = int(data.get("aires_nc") or 0)

    registro.observacion = data.get("observacion", "")

    # 🔥 recalcular total
    registro.total = calcular_total(data)

    db.commit()
    db.refresh(registro)

    return {
        "mensaje": "Inspección actualizada correctamente",
        "id": registro.id,
        "total": registro.total
    }



# ======================================================
# ❌ ELIMINAR
# ======================================================
@router.delete("/{id}")
def eliminar_inspeccion(id: int, db: Session = Depends(get_db)):
    registro = db.query(InspeccionEnergia).filter(
        InspeccionEnergia.id == id
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