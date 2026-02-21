from pydantic import BaseModel
from datetime import date

class LecturaManualCreate(BaseModel):
    bodega: str
    lectura: int
    tipo: str   # "agua" | "energia"
    fecha: date
