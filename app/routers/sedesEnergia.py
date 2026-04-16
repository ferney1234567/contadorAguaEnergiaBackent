from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.sede_energia import SedeEnergia
from app.models.comparativo_energia import ComparativoEnergia

router = APIRouter(prefix="/sedes_energia", tags=["Sedes Energia"])


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

        existe = db.query(SedeEnergia).filter(SedeEnergia.nombre == nombre).first()

        if existe:
            raise HTTPException(status_code=400, detail="La sede ya existe")

        nueva = SedeEnergia(
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
    return db.query(SedeEnergia).order_by(SedeEnergia.nombre.asc()).all()


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
    sede = db.query(SedeEnergia).filter(SedeEnergia.id == id).first()

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
        sede = db.query(SedeEnergia).filter(SedeEnergia.id == id).first()

        if not sede:
            raise HTTPException(status_code=404, detail="Sede no encontrada")

        # 🔥 BORRAR PRIMERO LOS DATOS RELACIONADOS
        registros = db.query(ComparativoEnergia).filter(
           ComparativoEnergia.sede_energia == id
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