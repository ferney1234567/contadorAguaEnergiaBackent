from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.resmas import Resmas

router = APIRouter(prefix="/resmas", tags=["Resmas"])


# =======================
# ✅ CREAR REGISTRO
# =======================
@router.post("/")
def crear_o_actualizar_resma(data: dict = Body(...), db: Session = Depends(get_db)):

    area_id = data.get("area_id")
    anio = data.get("anio")
    mes = data.get("mes")

    if not area_id or not anio or not mes:
        raise HTTPException(400, "Faltan datos obligatorios")

    registro = db.query(Resmas).filter(
        Resmas.area_id == area_id,
        Resmas.anio == anio,
        Resmas.mes == mes
    ).first()

    # 🔥 SI YA EXISTE → ACTUALIZA
    if registro:
        registro.cantidad = data.get("cantidad", registro.cantidad)

        db.commit()
        db.refresh(registro)

        return {"mensaje": "Registro actualizado"}

    # 🔥 SI NO EXISTE → CREA
    nuevo = Resmas(
        area_id=area_id,
        anio=anio,
        mes=mes,
        cantidad=data.get("cantidad", 0),
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {"mensaje": "Registro creado"}

# =======================
# 📄 LISTAR
# =======================
from fastapi import Query

# =======================
# 📄 LISTAR (FILTRADO POR AÑO)
# =======================
@router.get("/")
def listar_resmas(
    anio: int = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Resmas)

    # 🔥 FILTRO POR AÑO (CLAVE)
    if anio:
        query = query.filter(Resmas.anio == anio)

    data = query.all()

    return [
        {
            "id": r.id,
            "area_id": r.area_id,
            "anio": r.anio,
            "mes": r.mes,
            "cantidad": r.cantidad,
        }
        for r in data
    ]



# =======================
# ❌ ELIMINAR
# =======================
@router.delete("/{id}")
def eliminar_resma(id: int, db: Session = Depends(get_db)):
    registro = db.query(Resmas).filter(Resmas.id == id).first()

    if not registro:
        raise HTTPException(404, "Registro no encontrado")

    db.delete(registro)
    db.commit()

    return {"mensaje": "Eliminado correctamente"}