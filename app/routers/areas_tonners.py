from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.area_tonner import AreaTonner

router = APIRouter(prefix="/areas-tonners", tags=["Áreas Tonners"])


# =======================
# ✅ CREAR ÁREA
# =======================
@router.post("/")
def crear_area(data: dict = Body(...), db: Session = Depends(get_db)):
    nombre = data.get("nombre")

    if not nombre:
        raise HTTPException(400, "El nombre es obligatorio")

    existe = db.query(AreaTonner).filter(AreaTonner.nombre == nombre).first()

    if existe:
        raise HTTPException(400, "El área ya existe")

    nueva = AreaTonner(nombre=nombre)

    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    return {"mensaje": "Área creada"}


# =======================
# 📄 LISTAR ÁREAS
# =======================
@router.get("/")
def listar_areas(db: Session = Depends(get_db)):
    data = db.query(AreaTonner).all()

    return [
        {
            "id": a.id,
            "nombre": a.nombre,
        }
        for a in data
    ]


# =======================
# ✏️ EDITAR ÁREA
# =======================
@router.put("/")
def editar_area(data: dict = Body(...), db: Session = Depends(get_db)):
    id = data.get("id")
    nombre = data.get("nombre")

    if not id or not nombre:
        raise HTTPException(400, "Datos incompletos")

    area = db.query(AreaTonner).filter(AreaTonner.id == id).first()

    if not area:
        raise HTTPException(404, "Área no encontrada")

    area.nombre = nombre

    db.commit()
    db.refresh(area)

    return {"mensaje": "Área actualizada"}


# =======================
# ❌ ELIMINAR ÁREA
# =======================
@router.delete("/")
def eliminar_area(id: int, db: Session = Depends(get_db)):
    area = db.query(AreaTonner).filter(AreaTonner.id == id).first()

    if not area:
        raise HTTPException(404, "Área no encontrada")

    db.delete(area)
    db.commit()

    return {"mensaje": "Área eliminada"}