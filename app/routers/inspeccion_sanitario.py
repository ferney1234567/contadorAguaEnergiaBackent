from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.inspeccion_agua import InspeccionSanitaria
from app.models.area_sanitaria import AreaSanitaria
from sqlalchemy import func

router = APIRouter(
    prefix="/inspecciones-sanitarias",
    tags=["Sanitarios"]
)

# ======================================================
# 🧠 CALCULAR TOTAL
# ======================================================
def calcular_total(data):
    return (
        int(data.get("sanitarios_c") or 0) +
        int(data.get("orinales_c") or 0) +
        int(data.get("duchas_c") or 0) +
        int(data.get("lavamanos_c") or 0) +
        int(data.get("llaves_c") or 0)
    )


# ======================================================
# 🔥 UPSERT (IGUAL QUE RECICLAJE)
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
    area = db.query(AreaSanitaria).filter(AreaSanitaria.id == area_id).first()
    if not area:
        raise HTTPException(404, "El área sanitaria no existe")

    # ======================================================
    # 🔥 BUSCAR SI YA EXISTE
    # ======================================================
    registro = db.query(InspeccionSanitaria).filter(
        InspeccionSanitaria.fecha == fecha,
        InspeccionSanitaria.responsable == responsable,
        InspeccionSanitaria.area_id == area_id
    ).first()

    total = calcular_total(data)

    # ======================================================
    # ✏️ UPDATE
    # ======================================================
    if registro:
        registro.sanitarios_c = int(data.get("sanitarios_c") or 0)
        registro.sanitarios_nc = int(data.get("sanitarios_nc") or 0)

        registro.orinales_c = int(data.get("orinales_c") or 0)
        registro.orinales_nc = int(data.get("orinales_nc") or 0)

        registro.duchas_c = int(data.get("duchas_c") or 0)
        registro.duchas_nc = int(data.get("duchas_nc") or 0)

        registro.lavamanos_c = int(data.get("lavamanos_c") or 0)
        registro.lavamanos_nc = int(data.get("lavamanos_nc") or 0)

        registro.llaves_c = int(data.get("llaves_c") or 0)
        registro.llaves_nc = int(data.get("llaves_nc") or 0)

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
    nueva = InspeccionSanitaria(
        fecha=fecha,
        responsable=responsable,
        area_id=area_id,

        sanitarios_c=int(data.get("sanitarios_c") or 0),
        sanitarios_nc=int(data.get("sanitarios_nc") or 0),

        orinales_c=int(data.get("orinales_c") or 0),
        orinales_nc=int(data.get("orinales_nc") or 0),

        duchas_c=int(data.get("duchas_c") or 0),
        duchas_nc=int(data.get("duchas_nc") or 0),

        lavamanos_c=int(data.get("lavamanos_c") or 0),
        lavamanos_nc=int(data.get("lavamanos_nc") or 0),

        llaves_c=int(data.get("llaves_c") or 0),
        llaves_nc=int(data.get("llaves_nc") or 0),

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
    registros = db.query(InspeccionSanitaria).all()

    return [
        {
            "id": r.id,
            "fecha": r.fecha,
            "responsable": r.responsable,
            "area_id": r.area_id,
            "area": r.area.nombre if r.area else None,

            "sanitarios_c": r.sanitarios_c,
            "sanitarios_nc": r.sanitarios_nc,

            "orinales_c": r.orinales_c,
            "orinales_nc": r.orinales_nc,

            "duchas_c": r.duchas_c,
            "duchas_nc": r.duchas_nc,

            "lavamanos_c": r.lavamanos_c,
            "lavamanos_nc": r.lavamanos_nc,

            "llaves_c": r.llaves_c,
            "llaves_nc": r.llaves_nc,

            "observacion": r.observacion,
            "total": r.total
        }
        for r in registros
    ]


# ======================================================
# ❌ DELETE
# ======================================================
@router.delete("/")
def eliminar_inspeccion_sanitaria(data: dict = Body(...), db: Session = Depends(get_db)):
    responsable = data.get("responsable")
    fecha = data.get("fecha")

    if not responsable or not fecha:
        raise HTTPException(400, "Faltan datos")

    registros = db.query(InspeccionSanitaria).filter(
        InspeccionSanitaria.responsable == responsable,
        func.date(InspeccionSanitaria.fecha) == fecha
    ).all()

    if not registros:
        raise HTTPException(404, "No se encontraron registros")

    for r in registros:
        db.delete(r)

    db.commit()

    return {"mensaje": "Inspección eliminada correctamente"}