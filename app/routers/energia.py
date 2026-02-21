from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Body, Query


from app.database.session import get_db
from app.models.consumo_energia import ConsumoEnergia

router = APIRouter(prefix="/energia", tags=["Energia"])


# ==========================================================
# CREAR O ACTUALIZAR CONSUMO DE ENERGÍA (UPSERT POR FECHA)
# ==========================================================
@router.post("/")
def crear_o_actualizar_consumo_energia(
    fecha: date = Body(...),
    bodega1: int = Body(...),
    bodega2: int = Body(...),
    total_bodega1: float = Body(...),
    total_bodega2: float = Body(...),
    db: Session = Depends(get_db)
):
    """
    ✔ Crea o actualiza consumo diario de energía
    ✔ UN SOLO registro por fecha
    ✔ Sin duplicados
    ✔ No maneja metas
    """

    # 🔍 Buscar si ya existe consumo para ese día
    registro = (
        db.query(ConsumoEnergia)
        .filter(ConsumoEnergia.fecha == fecha)
        .first()
    )

    if registro:
        # 🔄 ACTUALIZAR
        registro.bodega1 = bodega1
        registro.bodega2 = bodega2
        registro.total_bodega1 = total_bodega1
        registro.total_bodega2 = total_bodega2
        registro.sumatoria = total_bodega1 + total_bodega2
    else:
        # ➕ CREAR
        registro = ConsumoEnergia(
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
def listar_consumo_energia(db: Session = Depends(get_db)):
    return (
        db.query(ConsumoEnergia)
        .order_by(ConsumoEnergia.fecha.asc())
        .all()
    )


# ==========================================================
# LISTAR CONSUMO + META MENSUAL (JOIN LÓGICO)
# 👉 ESTE ES EL QUE USA TU DASHBOARD
# ==========================================================
@router.get("/con-meta")
def listar_consumo_energia_con_meta(db: Session = Depends(get_db)):
    """
    Devuelve:
    - Consumo diario de energía
    - Meta mensual correspondiente (si existe)

    Relación por:
    YEAR(fecha) + MONTH(fecha) + tipo='energia'
    """

    query = db.execute(
        text("""
            SELECT
                ce.id,
                ce.fecha,
                ce.bodega1,
                ce.bodega2,
                ce.total_bodega1,
                ce.total_bodega2,
                ce.sumatoria,
                ce.created_at,
                ce.updated_at,
                m.meta AS meta_mensual
            FROM consumo_energia ce
            LEFT JOIN metas m
              ON m.tipo = 'energia'
             AND m.anio = YEAR(ce.fecha)
             AND m.mes  = MONTH(ce.fecha)
            ORDER BY ce.fecha ASC
        """)
    )

    return [dict(row) for row in query.mappings()]


# ==========================================================
# OBTENER REGISTRO POR ID
# ==========================================================
@router.get("/{energia_id}")
def obtener_consumo_energia(energia_id: int, db: Session = Depends(get_db)):
    registro = db.query(ConsumoEnergia).get(energia_id)

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    return registro


# ==========================================================
# ELIMINAR REGISTRO
# ==========================================================
@router.delete("/")
def eliminar_consumo_por_bodega(
    fecha: date = Query(...),
    bodega: int = Query(...),
    db: Session = Depends(get_db)
):
    registro = (
        db.query(ConsumoEnergia)
        .filter(ConsumoEnergia.fecha == fecha)
        .first()
    )

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # 🧹 Normalizar NULL → 0
    registro.bodega1 = registro.bodega1 or 0
    registro.bodega2 = registro.bodega2 or 0
    registro.total_bodega1 = registro.total_bodega1 or 0
    registro.total_bodega2 = registro.total_bodega2 or 0

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
        (registro.total_bodega1 or 0) +
        (registro.total_bodega2 or 0)
    )

    # ❌ Si ambas bodegas quedaron en 0 → eliminar fila
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
