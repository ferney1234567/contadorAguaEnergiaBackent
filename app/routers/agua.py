from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Body,Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import get_db
from app.models.consumo_agua import ConsumoAgua

router = APIRouter(prefix="/agua", tags=["Agua"])


# ==========================================================
# CREAR MÚLTIPLES REGISTROS POR FECHA
# ==========================================================
@router.post("/")
def crear_consumo_agua(
    fecha: date = Body(...),
    bodega1: int = Body(...),
    bodega2: int = Body(...),
    total_bodega1: float = Body(...),
    total_bodega2: float = Body(...),
    db: Session = Depends(get_db)
):
    """
    ✔ Permite múltiples registros por misma fecha
    ✔ Crea nuevo registro siempre (sin duplicados)
    ✔ Si ambas bodegas son 0 → no crea registro
    """

    # Normalizar valores (evita None)
    bodega1 = bodega1 or 0
    bodega2 = bodega2 or 0
    total_bodega1 = total_bodega1 or 0
    total_bodega2 = total_bodega2 or 0

    # ❌ CASO: No crear si ambas bodegas son 0
    if bodega1 == 0 and bodega2 == 0:
        return {"created": False, "mensaje": "No se crea registro con ambas bodegas en 0"}

    # ➕ CREAR NUEVO REGISTRO (siempre)
    nuevo_registro = ConsumoAgua(
        fecha=fecha,
        bodega1=bodega1,
        bodega2=bodega2,
        total_bodega1=total_bodega1,
        total_bodega2=total_bodega2,
        sumatoria=total_bodega1 + total_bodega2,
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)

    return nuevo_registro


# ==========================================================
# LISTAR CONSUMO (SIN META)
# ==========================================================
@router.get("/")
def listar_consumo_agua(db: Session = Depends(get_db)):
    return (
        db.query(ConsumoAgua)
        .order_by(ConsumoAgua.fecha.asc())
        .all()
    )


# ==========================================================
# LISTAR CONSUMO + META MENSUAL (USADO EN DASHBOARD)
# ==========================================================
@router.get("/con-meta")
def listar_consumo_con_meta(db: Session = Depends(get_db)):
    """
    Devuelve:
    - Consumo diario
    - Meta mensual correspondiente (si existe)
    Relación:
    YEAR(fecha) + MONTH(fecha) + tipo='agua'
    """

    query = db.execute(
        text("""
            SELECT
                ca.id,
                ca.fecha,
                ca.bodega1,
                ca.bodega2,
                ca.total_bodega1,
                ca.total_bodega2,
                ca.sumatoria,
                ca.created_at,
                ca.updated_at,
                m.meta AS meta_mensual
            FROM consumo_agua ca
            LEFT JOIN metas m
              ON m.tipo = 'agua'
             AND m.anio = YEAR(ca.fecha)
             AND m.mes  = MONTH(ca.fecha)
            ORDER BY ca.fecha ASC
        """)
    )

    return [dict(row) for row in query.mappings()]


# ==========================================================
# OBTENER REGISTRO POR ID
# ==========================================================
@router.get("/{agua_id}")
def obtener_consumo_agua(agua_id: int, db: Session = Depends(get_db)):
    registro = db.query(ConsumoAgua).get(agua_id)

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    return registro


# ==========================================================
# ELIMINAR REGISTRO (MANUAL)
# ==========================================================

# ==========================================================
# ELIMINAR CONSUMO POR FECHA + BODEGA (IGUAL A ENERGÍA)
# ==========================================================
@router.delete("/")
def eliminar_consumo_por_bodega(
    fecha: date = Query(...),
    bodega: int = Query(...),  # 1 o 2
    db: Session = Depends(get_db),
):
    registro = (
        db.query(ConsumoAgua)
        .filter(ConsumoAgua.fecha == fecha)
        .first()
    )

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # 🧹 Borrar solo la bodega indicada
    if bodega == 1:
        registro.bodega1 = 0
        registro.total_bodega1 = 0
    elif bodega == 2:
        registro.bodega2 = 0
        registro.total_bodega2 = 0
    else:
        raise HTTPException(status_code=400, detail="Bodega inválida")

    # 🔄 Recalcular sumatoria
    registro.sumatoria = (
        registro.total_bodega1 + registro.total_bodega2
    )

    # ❌ Si ambas bodegas quedaron en 0 → eliminar registro completo
    if registro.bodega1 == 0 and registro.bodega2 == 0:
        db.delete(registro)
        db.commit()
        return {"deleted": "all"}

    db.commit()
    db.refresh(registro)

    return {
        "deleted": f"bodega_{bodega}",
        "registro": registro
    }