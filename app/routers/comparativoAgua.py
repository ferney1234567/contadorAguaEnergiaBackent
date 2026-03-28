from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.comparativo_agua import ComparativoAgua

router = APIRouter(prefix="/comparativoAgua", tags=["Comparativo Agua"])


# ==========================================================
# CREAR
# ==========================================================
@router.post("/")
def crear_comparativo_agua(
    nombre: str = Body(...),
    ubicacion: str = Body(...),
    cuenta: str = Body(...),
    anio: int = Body(...),
    mes: int = Body(...),
    m3_consumidos: float = Body(None),
    valor_consumo_agua: float = Body(None),
    cumple: bool = Body(True),
    db: Session = Depends(get_db)
):
    try:
        nuevo = ComparativoAgua(
            nombre=nombre,
            ubicacion=ubicacion,
            cuenta=cuenta,
            anio=anio,
            mes=mes,
            m3_consumidos=m3_consumidos,
            valor_consumo_agua=valor_consumo_agua,
            cumple=cumple,
        )

        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)

        return {"mensaje": "Registro creado", "data": nuevo}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# ACTUALIZAR
# ==========================================================
@router.put("/")
def actualizar_comparativo_agua(
    id: int = Body(...),
    nombre: str = Body(...),
    ubicacion: str = Body(...),
    cuenta: str = Body(...),
    anio: int = Body(...),
    mes: int = Body(...),
    m3_consumidos: float = Body(None),
    valor_consumo_agua: float = Body(None),
    cumple: bool = Body(True),
    db: Session = Depends(get_db)
):
    registro = db.query(ComparativoAgua).filter(
        ComparativoAgua.id == id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    registro.nombre = nombre
    registro.ubicacion = ubicacion
    registro.cuenta = cuenta
    registro.m3_consumidos = m3_consumidos
    registro.valor_consumo_agua = valor_consumo_agua
    registro.cumple = cumple

    db.commit()
    db.refresh(registro)

    return {"mensaje": "Actualizado"}
# ==========================================================
# LISTAR
# ==========================================================
@router.get("/")
def listar_comparativos_agua(db: Session = Depends(get_db)):
    return db.query(ComparativoAgua).order_by(
        ComparativoAgua.anio.asc(),
        ComparativoAgua.mes.asc(),
        ComparativoAgua.id.asc()
    ).all()


# ==========================================================
# ELIMINAR (🔥 ADAPTADO A TU FRONTEND)
# ==========================================================
@router.delete("/")
def eliminar_comparativo_agua(
    nombre: str = Body(...),
    anio: int = Body(...),
    mes: int = Body(...),
    db: Session = Depends(get_db)
):
    try:
        registro = db.query(ComparativoAgua).filter(
            ComparativoAgua.nombre == nombre,
            ComparativoAgua.anio == anio,
            ComparativoAgua.mes == mes
        ).first()

        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        db.delete(registro)
        db.commit()

        return {"mensaje": "Registro eliminado"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# OBTENER POR ID (opcional)
# ==========================================================
@router.get("/{comparativo_id}")
def obtener_comparativo_agua(comparativo_id: int, db: Session = Depends(get_db)):

    registro = db.query(ComparativoAgua).filter(
        ComparativoAgua.id == comparativo_id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Comparativo no encontrado")

    return registro