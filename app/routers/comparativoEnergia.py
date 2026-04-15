from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.comparativo_energia import ComparativoEnergia

router = APIRouter(prefix="/comparativoEnergia", tags=["Comparativo Energía"])


# ==========================================================
# 🔥 CREAR / ACTUALIZAR (UPSERT)
# ==========================================================
@router.post("/")
def guardar_comparativo_energia(
    sede_energia: int = Body(...),  # 🔥 CAMBIO
    anio: int = Body(...),
    mes: int = Body(...),
    kw_consumidos: float = Body(None),
    valor_consumo_energia: float = Body(None),
    cumple: bool = Body(True),
    db: Session = Depends(get_db)
):
    try:

        registro = db.query(ComparativoEnergia).filter(
            ComparativoEnergia.sede_energia == sede_energia,  # 🔥 CAMBIO
            ComparativoEnergia.anio == anio,
            ComparativoEnergia.mes == mes
        ).first()

        if registro:
            # UPDATE
            registro.kw_consumidos = kw_consumidos
            registro.valor_consumo_energia = valor_consumo_energia
            registro.cumple = cumple

            db.commit()
            db.refresh(registro)

            return {"mensaje": "Actualizado"}

        else:
            # CREATE
            nuevo = ComparativoEnergia(
                sede_energia=sede_energia,  # 🔥 CAMBIO
                anio=anio,
                mes=mes,
                kw_consumidos=kw_consumidos,
                valor_consumo_energia=valor_consumo_energia,
                cumple=cumple
            )

            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)

            return {"mensaje": "Creado"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


# ==========================================================
# 🔥 LISTAR TODOS
# ==========================================================
@router.get("/")
def listar_comparativos_energia(db: Session = Depends(get_db)):
    return db.query(ComparativoEnergia).order_by(
        ComparativoEnergia.anio.asc(),
        ComparativoEnergia.mes.asc(),
        ComparativoEnergia.sede_energia.asc()  # 🔥 CAMBIO
    ).all()


# ==========================================================
# 🔥 OBTENER POR ID
# ==========================================================
@router.get("/{comparativo_id}")
def obtener_comparativo_energia(comparativo_id: int, db: Session = Depends(get_db)):

    registro = db.query(ComparativoEnergia).filter(
        ComparativoEnergia.id == comparativo_id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    return registro


# ==========================================================
# 🔥 ELIMINAR POR ID
# ==========================================================
@router.delete("/{comparativo_id}")
def eliminar_comparativo_energia(comparativo_id: int, db: Session = Depends(get_db)):

    try:
        registro = db.query(ComparativoEnergia).filter(
            ComparativoEnergia.id == comparativo_id
        ).first()

        if not registro:
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        db.delete(registro)
        db.commit()

        return {"mensaje": "Eliminado correctamente"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


# ==========================================================
# 🔥 ELIMINAR POR SEDE
# ==========================================================
@router.delete("/por-sede/{sede_energia}")
def eliminar_por_sede(sede_energia: int, db: Session = Depends(get_db)):

    try:
        db.query(ComparativoEnergia).filter(
            ComparativoEnergia.sede_energia == sede_energia  # 🔥 CAMBIO
        ).delete()

        db.commit()

        return {"mensaje": "Registros eliminados por sede"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando por sede: {str(e)}"
        )