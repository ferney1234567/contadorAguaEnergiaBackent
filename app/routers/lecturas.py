from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database.session import get_db
from app.models.consumo_agua import ConsumoAgua
from app.models.consumo_energia import ConsumoEnergia
from app.schemas.lectura_manual import LecturaManualCreate

# ======================================================
# ROUTER
# ======================================================

router = APIRouter(
    prefix="/lecturas",
    tags=["Lecturas"]
)

# ======================================================
# CONSTANTES
# ======================================================

FACTOR_CONVERSION = 10  # 10 unidades = 1 m³

# ======================================================
# HELPERS
# ======================================================

def obtener_dia_habil_anterior_agua(db: Session, fecha: date):
    return (
        db.query(ConsumoAgua)
        .filter(ConsumoAgua.fecha < fecha)
        .filter(
            (ConsumoAgua.bodega1 > 0) |
            (ConsumoAgua.bodega2 > 0)
        )
        .order_by(ConsumoAgua.fecha.desc())
        .first()
    )


def obtener_dia_habil_anterior_energia(db: Session, fecha: date):
    return (
        db.query(ConsumoEnergia)
        .filter(ConsumoEnergia.fecha < fecha)
        .filter(
            (ConsumoEnergia.bodega1 > 0) |
            (ConsumoEnergia.bodega2 > 0)
        )
        .order_by(ConsumoEnergia.fecha.desc())
        .first()
    )

# ======================================================
# ENDPOINT
# ======================================================

@router.post("/manual")
def guardar_lectura_manual(
    data: LecturaManualCreate,
    db: Session = Depends(get_db)
):
    bodega = data.bodega
    lectura = data.lectura
    tipo = data.tipo
    fecha = data.fecha

    # ==================================================
    # VALIDACIÓN GENERAL
    # ==================================================

    if lectura <= 0:
        raise HTTPException(
            status_code=400,
            detail="La lectura debe ser mayor a cero"
        )

    # ==================================================
    # AGUA
    # ==================================================
    if tipo == "agua":

        registro = db.query(ConsumoAgua).filter(
            ConsumoAgua.fecha == fecha
        ).first()

        if not registro:
            registro = ConsumoAgua(
                fecha=fecha,
                bodega1=0,
                bodega2=0,
                total_bodega1=0,
                total_bodega2=0,
                sumatoria=0
            )
            db.add(registro)

        anterior = obtener_dia_habil_anterior_agua(db, fecha)

        # -------- BODEGA 2 --------
        if "bodega_2" in bodega:
            registro.bodega1 = lectura
            if anterior and anterior.bodega1 > 0:
                registro.total_bodega1 = (
                    (lectura - anterior.bodega1) / FACTOR_CONVERSION
                )
            else:
                registro.total_bodega1 = 0

        # -------- BODEGA 4 --------
        if "bodega_4" in bodega:
            registro.bodega2 = lectura
            if anterior and anterior.bodega2 > 0:
                registro.total_bodega2 = (
                    (lectura - anterior.bodega2) / FACTOR_CONVERSION
                )
            else:
                registro.total_bodega2 = 0

        registro.sumatoria = (
            registro.total_bodega1 + registro.total_bodega2
        )

    # ==================================================
    # ENERGÍA
    # ==================================================
    elif tipo == "energia":

        registro = db.query(ConsumoEnergia).filter(
            ConsumoEnergia.fecha == fecha
        ).first()

        if not registro:
            registro = ConsumoEnergia(
                fecha=fecha,
                bodega1=0,
                bodega2=0,
                total_bodega1=0,
                total_bodega2=0,
                sumatoria=0
            )
            db.add(registro)

        anterior = obtener_dia_habil_anterior_energia(db, fecha)

        # -------- BODEGA 1 --------
        if "bodega_1" in bodega:
            registro.bodega1 = lectura
            if anterior and anterior.bodega1 > 0:
                if lectura < anterior.bodega1:
                    raise HTTPException(
                        status_code=400,
                        detail="La lectura de energía no puede ser menor a la anterior"
                    )
                registro.total_bodega1 = lectura - anterior.bodega1
            else:
                registro.total_bodega1 = 0

        # -------- BODEGA 3 --------
        if "bodega_3" in bodega:
            registro.bodega2 = lectura
            if anterior and anterior.bodega2 > 0:
                if lectura < anterior.bodega2:
                    raise HTTPException(
                        status_code=400,
                        detail="La lectura de energía no puede ser menor a la anterior"
                    )
                registro.total_bodega2 = lectura - anterior.bodega2
            else:
                registro.total_bodega2 = 0

        registro.sumatoria = (
            registro.total_bodega1 + registro.total_bodega2
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Tipo inválido"
        )

    # ==================================================
    # COMMIT
    # ==================================================

    db.commit()
    db.refresh(registro)

    return {
        "ok": True,
        "mensaje": "Lectura guardada / actualizada correctamente",
        "fecha": str(fecha),
        "id": registro.id
    }
