from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.models.comparativo_agua import ComparativoAgua
from app.models.sede import Sede

router = APIRouter(prefix="/comparativoAgua", tags=["Comparativo Agua"])


# ==========================================================
# 🔥 UPSERT (CREAR O ACTUALIZAR)
# ==========================================================
@router.post("/")
def guardar_comparativo(
    sede_id: int = Body(...),
    anio: int = Body(...),
    mes: int = Body(...),
    m3_consumidos: float = Body(None),
    valor_consumo_agua: float = Body(None),
    cumple: bool = Body(True),
    db: Session = Depends(get_db)
):
    try:

        # validar sede
        sede = db.query(Sede).filter(Sede.id == sede_id).first()
        if not sede:
            raise HTTPException(status_code=404, detail="Sede no existe")

        # 🔥 UPSERT REAL
        registro = db.query(ComparativoAgua).filter(
            ComparativoAgua.sede_id == sede_id,
            ComparativoAgua.anio == anio,
            ComparativoAgua.mes == mes
        ).first()

        if registro:
            registro.m3_consumidos = m3_consumidos
            registro.valor_consumo_agua = valor_consumo_agua
            registro.cumple = cumple

            db.commit()
            db.refresh(registro)

            return {"mensaje": "Actualizado", "data": registro}

        else:
            nuevo = ComparativoAgua(
                sede_id=sede_id,
                anio=anio,
                mes=mes,
                m3_consumidos=m3_consumidos,
                valor_consumo_agua=valor_consumo_agua,
                cumple=cumple,
            )

            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)

            return {"mensaje": "Creado", "data": nuevo}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# 📊 LISTAR (CON DATOS DE SEDE)
# ==========================================================
@router.get("/")
def listar_comparativo(db: Session = Depends(get_db)):

    registros = db.query(ComparativoAgua).options(
        joinedload(ComparativoAgua.sede)
    ).all()

    resultado = []

    for r in registros:
        resultado.append({
            "id": r.id,
            "sede_id": r.sede_id,
            "nombre": r.sede.nombre,
            "ubicacion": r.sede.ubicacion,
            "cuenta": r.sede.cuenta,
            "anio": r.anio,
            "mes": r.mes,
            "m3_consumidos": r.m3_consumidos,
            "valor_consumo_agua": r.valor_consumo_agua,
            "cumple": r.cumple
        })

    return resultado


# ==========================================================
# ✏️ ACTUALIZAR (POR ID)
# ==========================================================
@router.put("/{id}")
def actualizar(
    id: int,
    m3_consumidos: float = Body(None),
    valor_consumo_agua: float = Body(None),
    cumple: bool = Body(True),
    db: Session = Depends(get_db)
):
    registro = db.query(ComparativoAgua).filter(
        ComparativoAgua.id == id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="No encontrado")

    registro.m3_consumidos = m3_consumidos
    registro.valor_consumo_agua = valor_consumo_agua
    registro.cumple = cumple

    db.commit()
    db.refresh(registro)

    return {"mensaje": "Actualizado"}


# ==========================================================
# 🗑️ ELIMINAR POR ID
# ==========================================================
@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db)):

    registro = db.query(ComparativoAgua).filter(
        ComparativoAgua.id == id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="No encontrado")

    db.delete(registro)
    db.commit()

    return {"mensaje": "Eliminado correctamente"}


# ==========================================================
# 🔍 OBTENER POR ID
# ==========================================================
@router.get("/{comparativo_id}")
def obtener(comparativo_id: int, db: Session = Depends(get_db)):

    registro = db.query(ComparativoAgua).options(
        joinedload(ComparativoAgua.sede)
    ).filter(
        ComparativoAgua.id == comparativo_id
    ).first()

    if not registro:
        raise HTTPException(status_code=404, detail="No encontrado")

    return {
        "id": registro.id,
        "sede_id": registro.sede_id,
        "nombre": registro.sede.nombre,
        "ubicacion": registro.sede.ubicacion,
        "cuenta": registro.sede.cuenta,
        "anio": registro.anio,
        "mes": registro.mes,
        "m3_consumidos": registro.m3_consumidos,
        "valor_consumo_agua": registro.valor_consumo_agua,
        "cumple": registro.cumple
    }


# ==========================================================
# 🚀 GENERAR AÑO COMPLETO (PRO)
# ==========================================================
@router.post("/generar-anio")
def generar_anio(anio: int, db: Session = Depends(get_db)):

    try:

        # 🔥 traer TODAS las sedes
        sedes = db.query(Sede).all()

        if not sedes:
            raise HTTPException(status_code=400, detail="No hay sedes creadas")

        for sede in sedes:
            for mes in range(1, 13):

                existe = db.query(ComparativoAgua).filter(
                    ComparativoAgua.sede_id == sede.id,
                    ComparativoAgua.anio == anio,
                    ComparativoAgua.mes == mes
                ).first()

                if not existe:
                    nuevo = ComparativoAgua(
                        sede_id=sede.id,
                        anio=anio,
                        mes=mes,
                        m3_consumidos=0,
                        valor_consumo_agua=0,
                        cumple=True
                    )
                    db.add(nuevo)

        db.commit()

        return {"mensaje": f"Año {anio} generado correctamente"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))