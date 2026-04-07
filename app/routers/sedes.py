from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.sede import Sede
from app.models.comparativo_agua import ComparativoAgua

router = APIRouter(prefix="/sedes", tags=["Sedes"])


# ============================================
# CREAR SEDE
# ============================================
@router.post("/")
def crear_sede(
    nombre: str = Body(...),
    ubicacion: str = Body(...),
    cuenta: str = Body(...),
    db: Session = Depends(get_db)
):
    try:

        existe = db.query(Sede).filter(Sede.nombre == nombre).first()

        if existe:
            raise HTTPException(status_code=400, detail="La sede ya existe")

        nueva = Sede(
            nombre=nombre,
            ubicacion=ubicacion,
            cuenta=cuenta
        )

        db.add(nueva)
        db.commit()
        db.refresh(nueva)

        return {"mensaje": "Sede creada", "data": nueva}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# LISTAR SEDES
# ============================================
@router.get("/")
def listar_sedes(db: Session = Depends(get_db)):
    return db.query(Sede).order_by(Sede.nombre.asc()).all()


# ============================================
# ACTUALIZAR SEDE
# ============================================
@router.put("/{id}")
def actualizar_sede(
    id: int,
    nombre: str = Body(...),
    ubicacion: str = Body(...),
    cuenta: str = Body(...),
    db: Session = Depends(get_db)
):
    sede = db.query(Sede).filter(Sede.id == id).first()

    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")

    sede.nombre = nombre
    sede.ubicacion = ubicacion
    sede.cuenta = cuenta

    db.commit()
    db.refresh(sede)

    return {"mensaje": "Sede actualizada"}


# ============================================
# ELIMINAR SEDE
# ============================================

@router.delete("/{id}")
def eliminar_sede(id: int, db: Session = Depends(get_db)):

    try:
        sede = db.query(Sede).filter(Sede.id == id).first()

        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        # 🔥 BORRAR PRIMERO LOS DATOS RELACIONADOS
        registros = db.query(ComparativoAgua).filter(
            ComparativoAgua.sede_id == id
        ).all()

        for r in registros:
            db.delete(r)

        db.commit()  # 🔥 IMPORTANTE

        # 🔥 AHORA SÍ BORRAR LA SEDE
        db.delete(sede)
        db.commit()

        return {"mensaje": "Sede eliminada correctamente"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))