from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Body,Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import get_db
from app.models.consumo_agua import ConsumoAgua

router = APIRouter(prefix="/agua", tags=["Agua"])


# ==========================================================
# CREAR / ACTUALIZAR / ELIMINAR CONSUMO DE AGUA
# ==========================================================
@router.post("/")
def crear_o_actualizar_consumo_agua(
    fecha: date = Body(...),
    bodega1: int = Body(...),
    bodega2: int = Body(...),
    total_bodega1: float = Body(...),
    total_bodega2: float = Body(...),
    db: Session = Depends(get_db)
):
    """
    ✔ 1 solo registro por fecha
    ✔ Si una bodega es 0 → se actualiza
    ✔ Si ambas bodegas son 0 → se elimina el registro
    ✔ No rompe dashboard ni metas
    """

    # Normalizar valores (evita None)
    bodega1 = bodega1 or 0
    bodega2 = bodega2 or 0
    total_bodega1 = total_bodega1 or 0
    total_bodega2 = total_bodega2 or 0

    # 🔍 Buscar registro existente
    registro = (
        db.query(ConsumoAgua)
        .filter(ConsumoAgua.fecha == fecha)
        .first()
    )

    # ======================================================
    # ❌ CASO: BORRAR TODO (ambas bodegas en 0)
    # ======================================================
    if bodega1 == 0 and bodega2 == 0:
        if registro:
            db.delete(registro)
            db.commit()
            return {
                "deleted": True,
                "fecha": fecha
            }

        return {
            "deleted": False,
            "mensaje": "No existía registro para eliminar"
        }

    # ======================================================
    # 🔄 CASO: ACTUALIZAR
    # ======================================================
    if registro:
        registro.bodega1 = bodega1
        registro.bodega2 = bodega2
        registro.total_bodega1 = total_bodega1
        registro.total_bodega2 = total_bodega2
        registro.sumatoria = total_bodega1 + total_bodega2

    # ======================================================
    # ➕ CASO: CREAR
    # ======================================================
    else:
        registro = ConsumoAgua(
            fecha=fecha,
            bodega1=bodega1,
            bodega2=bodega2,
            total_bodega1=total_bodega1,
            total_bodega2=total_bodega2,
            sumatoria=total_bodega1 + total_bodega2,
        )
        db.add(registro)

    db.commit()
    db.refresh(registro)

    return registro


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