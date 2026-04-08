from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.tonner import Tonner

router = APIRouter(prefix="/tonners", tags=["Tonners"])


# =======================
# ✅ CREAR O ACTUALIZAR
# =======================
@router.post("/")
def crear_o_actualizar_tonner(data: dict = Body(...), db: Session = Depends(get_db)):

    area_id = data.get("area_id")
    modelo_tonner = data.get("modelo_tonner")
    fecha = data.get("fecha")

    if not area_id or not modelo_tonner or not fecha:
        raise HTTPException(400, "Faltan datos obligatorios")

    # 🔥 BUSCAR SI YA EXISTE
    registro = db.query(Tonner).filter(
        Tonner.area_id == area_id,
        Tonner.modelo_tonner == modelo_tonner,
        Tonner.fecha == fecha
    ).first()

    # 🔥 SI EXISTE → ACTUALIZA
    if registro:
        registro.responsable = data.get("responsable", registro.responsable)
        registro.modelo_impresora = data.get("modelo_impresora", registro.modelo_impresora)
        registro.cantidad = data.get("cantidad", registro.cantidad)

        db.commit()
        db.refresh(registro)

        return {"mensaje": "Registro actualizado"}

    # 🔥 SI NO EXISTE → CREA
    nuevo = Tonner(
        area_id=area_id,
        responsable=data.get("responsable"),
        modelo_tonner=modelo_tonner,
        modelo_impresora=data.get("modelo_impresora"),
        cantidad=data.get("cantidad", 1),
        fecha=fecha,
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {"mensaje": "Registro creado"}


# =======================
# 📄 LISTAR TONNERS
# =======================
@router.get("/")
def listar_tonners(
    fecha: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Tonner)

    # 🔥 FILTRO OPCIONAL POR FECHA
    if fecha:
        query = query.filter(Tonner.fecha == fecha)

    data = query.all()

    return [
        {
            "id": t.id,
            "area_id": t.area_id,
            "responsable": t.responsable,
            "modelo_tonner": t.modelo_tonner,
            "modelo_impresora": t.modelo_impresora,
            "cantidad": t.cantidad,
            "fecha": t.fecha,
        }
        for t in data
    ]
    
@router.put("/{id}")
def actualizar_tonner(id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    registro = db.query(Tonner).filter(Tonner.id == id).first()

    if not registro:
        raise HTTPException(404, "Registro no encontrado")

    registro.area_id = data.get("area_id", registro.area_id)
    registro.responsable = data.get("responsable", registro.responsable)
    registro.modelo_tonner = data.get("modelo_tonner", registro.modelo_tonner)
    registro.modelo_impresora = data.get("modelo_impresora", registro.modelo_impresora)
    registro.cantidad = data.get("cantidad", registro.cantidad)
    registro.fecha = data.get("fecha", registro.fecha)

    db.commit()
    db.refresh(registro)

    return {"mensaje": "Actualizado correctamente"}
# =======================
# ❌ ELIMINAR TONNER
# =======================
@router.delete("/{id}")
def eliminar_tonner(id: int, db: Session = Depends(get_db)):
    registro = db.query(Tonner).filter(Tonner.id == id).first()

    if not registro:
        raise HTTPException(404, "Registro no encontrado")

    db.delete(registro)
    db.commit()

    return {"mensaje": "Eliminado correctamente"}