from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.meta import Meta

router = APIRouter(prefix="/metas", tags=["Metas"])


# ======================================================
# CREAR O ACTUALIZAR META (UPSERT POR MES)
# Esta meta será válida DESDE este mes en adelante
# ======================================================
@router.post("/")
def guardar_meta(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    tipo = data.get("tipo")
    anio = data.get("anio")
    mes = data.get("mes")
    meta = data.get("meta")

    if not all([tipo, anio, mes is not None, meta is not None]):
        raise HTTPException(
            status_code=400,
            detail="Faltan datos para guardar la meta"
        )

    # Buscar si ya existe meta para ese mes
    registro = (
        db.query(Meta)
        .filter(
            Meta.tipo == tipo,
            Meta.anio == anio,
            Meta.mes == mes
        )
        .first()
    )

    if registro:
        registro.meta = meta
    else:
        registro = Meta(
            tipo=tipo,
            anio=anio,
            mes=mes,
            meta=meta
        )
        db.add(registro)

    db.commit()
    db.refresh(registro)

    return {
        "tipo": registro.tipo,
        "anio": registro.anio,
        "mes": registro.mes,
        "meta": float(registro.meta),
        "mensaje": f"Meta guardada y vigente desde el mes {registro.mes}"
    }


# ======================================================
# OBTENER META VIGENTE POR MES
# Devuelve la última meta definida <= mes solicitado
# ======================================================
@router.get("/")
def obtener_meta(
    tipo: str,
    anio: int,
    mes: int,
    db: Session = Depends(get_db)
):
    """
    Ejemplo:
    - Meta creada en mayo (5)
    - Consulta junio (6)
    → devuelve meta de mayo
    """

    registro = (
        db.query(Meta)
        .filter(
            Meta.tipo == tipo,
            Meta.anio == anio,
            Meta.mes <= mes   # 🔥 CLAVE
        )
        .order_by(Meta.mes.desc())  # la más reciente
        .first()
    )

    if not registro:
        return {
            "meta": None,
            "vigente_desde": None
        }

    return {
        "meta": float(registro.meta),
        "vigente_desde": registro.mes
    }


# ======================================================
# OBTENER TODAS LAS METAS DEFINIDAS DE UN AÑO
# (para auditoría, reportes, gráficos, etc.)
# ======================================================
@router.get("/{anio}")
def obtener_metas_por_anio(
    anio: int,
    db: Session = Depends(get_db)
):
    metas = (
        db.query(Meta)
        .filter(Meta.anio == anio)
        .order_by(Meta.mes.asc())
        .all()
    )

    return [
        {
            "tipo": m.tipo,
            "anio": m.anio,
            "mes": m.mes,
            "meta": float(m.meta)
        }
        for m in metas
    ]
@router.delete("/")
def eliminar_meta_vigente(
    tipo: str,
    anio: int,
    mes: int,
    db: Session = Depends(get_db)
):
    # 🔍 Buscar la meta vigente (<= mes)
    registro = (
        db.query(Meta)
        .filter(
            Meta.tipo == tipo,
            Meta.anio == anio,
            Meta.mes <= mes
        )
        .order_by(Meta.mes.desc())
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="No hay meta vigente para eliminar"
        )

    db.delete(registro)
    db.commit()

    return {
        "mensaje": "Meta vigente eliminada correctamente",
        "tipo": registro.tipo,
        "anio": registro.anio,
        "mes_eliminado": registro.mes
    }

