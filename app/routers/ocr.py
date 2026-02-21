from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import cv2
import io
import re

# ======================================================
# ROUTER OCR
# ======================================================
router = APIRouter(
    prefix="/ocr",
    tags=["OCR"],
)

# ======================================================
# INICIALIZAR OCR (UNA SOLA VEZ)
# ======================================================
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en"   # números funcionan mejor con 'en'
)

# ======================================================
# ENDPOINT: LEER CONTADOR
# ======================================================
@router.post("/leer_contador")
async def leer_contador(file: UploadFile = File(...)):

    # --------------------
    # VALIDACIÓN DE ARCHIVO
    # --------------------
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo enviado no es una imagen válida"
        )

    contenido = await file.read()

    # --------------------
    # ABRIR IMAGEN
    # --------------------
    try:
        imagen = Image.open(io.BytesIO(contenido)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="No se pudo abrir la imagen"
        )

    img_np = np.array(imagen)

    # ======================================================
    # PREPROCESAMIENTO (MEJOR OCR)
    # ======================================================
    img = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    img = cv2.convertScaleAbs(img, alpha=1.8, beta=20)
    img = cv2.GaussianBlur(img, (3, 3), 0)

    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    img = cv2.filter2D(img, -1, kernel)

    img = cv2.adaptiveThreshold(
        img,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        21,
        10
    )

    # --------------------
    # RECORTE CENTRAL (DISPLAY)
    # --------------------
    h, w = img.shape
    recorte = img[
        int(h * 0.25):int(h * 0.75),
        int(w * 0.2):int(w * 0.8)
    ]

    # PaddleOCR requiere imagen RGB
    recorte_rgb = cv2.cvtColor(recorte, cv2.COLOR_GRAY2RGB)

    # ======================================================
    # OCR
    # ======================================================
    resultado = ocr.ocr(recorte_rgb)

    if not resultado or not resultado[0]:
        return JSONResponse({
            "lectura": None,
            "confianza": None,
            "mensaje": "No se detectó ningún texto"
        })

    textos = []
    confianzas = []

    for linea in resultado[0]:
        texto = linea[1][0]
        confianza = float(linea[1][1])

        # solo números
        numeros = re.sub(r"[^0-9]", "", texto)

        if numeros:
            textos.append(numeros)
            confianzas.append(confianza)

    if not textos:
        return JSONResponse({
            "lectura": None,
            "confianza": None,
            "mensaje": "No se detectaron números en el contador"
        })

    lectura_final = "".join(textos)
    confianza_final = round(sum(confianzas) / len(confianzas), 3)

    # ======================================================
    # RESPUESTA FINAL
    # ======================================================
    return JSONResponse({
        "lectura": lectura_final,
        "confianza": confianza_final,
        "mensaje": "Lectura detectada correctamente"
    })
