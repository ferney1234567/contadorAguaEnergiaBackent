from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.AreaEnergia import AreaEnergia
from app.models.inspeccion_energia import InspeccionEnergia

router = APIRouter(prefix="/areas-energia", tags=["Areas Energia"])


# =======================
# ✅ CREAR AREA
# =======================
@router.post("/")
def crear_area(data: dict = Body(...), db: Session = Depends(get_db)):
    nombre = (data.get("nombre") or "").strip()

    if not nombre:
        raise HTTPException(400, "El nombre es obligatorio")

    existe = db.query(AreaEnergia).filter(AreaEnergia.nombre == nombre).first()
    if existe:
        raise HTTPException(400, "El área ya existe")

    nueva = AreaEnergia(nombre=nombre)

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {"id": nueva.id, "nombre": nueva.nombre}


# =======================
# 📄 LISTAR AREAS
# =======================
@router.get("/")
def listar_areas(db: Session = Depends(get_db)):
    areas = db.query(AreaEnergia).order_by(AreaEnergia.nombre.asc()).all()

    return [{"id": a.id, "nombre": a.nombre} for a in areas]


# =======================
# 🔍 OBTENER AREA
# =======================
@router.get("/{id}")
def obtener_area(id: int, db: Session = Depends(get_db)):
    area = db.query(AreaEnergia).filter(AreaEnergia.id == id).first()

    if not area:
        raise HTTPException(404, "Área no encontrada")

    return {"id": area.id, "nombre": area.nombre}


# =======================
# ✏️ ACTUALIZAR AREA
# =======================
@router.put("/{id}")
def actualizar_area(id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    area = db.query(AreaEnergia).filter(AreaEnergia.id == id).first()

    if not area:
        raise HTTPException(404, "Área no encontrada")

    nombre = (data.get("nombre") or "").strip()

    if not nombre:
        raise HTTPException(400, "El nombre es obligatorio")

    existe = db.query(AreaEnergia).filter(
        AreaEnergia.nombre == nombre,
        AreaEnergia.id != id
    ).first()

    if existe:
        raise HTTPException(400, "Ya existe otra área con ese nombre")

    area.nombre = nombre

    db.commit()
    db.refresh(area)

    return {"id": area.id, "nombre": area.nombre}


# =======================
# ❌ ELIMINAR AREA
# =======================
@router.delete("/{id}")
def eliminar_area(id: int, db: Session = Depends(get_db)):
    area = db.query(AreaEnergia).filter(AreaEnergia.id == id).first()

    if not area:
        raise HTTPException(404, "Área no encontrada")

    # 🔥 ELIMINAR INSPECCIONES RELACIONADAS (ENERGIA)
    db.query(InspeccionEnergia).filter(
        InspeccionEnergia.area_id == id
    ).delete()

    # 🔥 ELIMINAR AREA
    db.delete(area)
    db.commit()

    return {"mensaje": "Área de energía eliminada correctamente"}