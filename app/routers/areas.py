from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.area import Area

router = APIRouter(prefix="/areas", tags=["Areas"])


# =======================
# ✅ CREAR AREA
# =========================
@router.post("/")
def crear_area(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    nombre = data.get("nombre")

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio"
        )

    existe = db.query(Area).filter(Area.nombre == nombre).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="El área ya existe"
        )

    nueva = Area(nombre=nombre)

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {
        "id": nueva.id,
        "nombre": nueva.nombre
    }


# =========================
# 📄 LISTAR AREAS
# =========================
@router.get("/")
def listar_areas(db: Session = Depends(get_db)):
    areas = db.query(Area).order_by(Area.nombre.asc()).all()

    return [
        {
            "id": a.id,
            "nombre": a.nombre
        }
        for a in areas
    ]


# =========================
# 🔍 OBTENER AREA
# =========================
@router.get("/{id}")
def obtener_area(id: int, db: Session = Depends(get_db)):
    area = db.query(Area).filter(Area.id == id).first()

    if not area:
        raise HTTPException(
            status_code=404,
            detail="Área no encontrada"
        )

    return {
        "id": area.id,
        "nombre": area.nombre
    }


# =========================
# ✏️ ACTUALIZAR AREA
# =========================
@router.put("/{id}")
def actualizar_area(
    id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    area = db.query(Area).filter(Area.id == id).first()

    if not area:
        raise HTTPException(
            status_code=404,
            detail="Área no encontrada"
        )

    nombre = data.get("nombre")

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio"
        )

    area.nombre = nombre

    db.commit()
    db.refresh(area)

    return {
        "id": area.id,
        "nombre": area.nombre
    }


# =========================
# ❌ ELIMINAR AREA
# =========================
@router.delete("/{id}")
def eliminar_area(id: int, db: Session = Depends(get_db)):
    area = db.query(Area).filter(Area.id == id).first()

    if not area:
        raise HTTPException(
            status_code=404,
            detail="Área no encontrada"
        )

    db.delete(area)
    db.commit()

    return {
        "mensaje": "Área eliminada correctamente",
        "id": id
    }