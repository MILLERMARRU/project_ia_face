
import streamlit as st
import easyocr
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from extractor import extraer_datos_ocr

@st.cache_resource
def cargar_lector():
    return easyocr.Reader(['es'], gpu=True)

reader = cargar_lector()

st.title("🎓 Lector de Carné Universitario")

# Elegir el modo de carga
modo = st.radio("Selecciona cómo cargar la imagen:", ["📷 Cámara", "📁 Subir archivo"])

imagen = None

if modo == "📷 Cámara":
    foto = st.camera_input("Captura tu carné")
    if foto:
        imagen = Image.open(foto).convert("RGB")

elif modo == "📁 Subir archivo":
    archivo = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])
    if archivo:
        imagen = Image.open(archivo).convert("RGB")

# Botón para procesar la imagen
if imagen and st.button("📄 Procesar imagen"):
    image_np = np.array(imagen)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    result = reader.readtext(image_bgr)
    texto_ocr = "\n".join([text for (_, text, _) in result])

    st.subheader("📝 Texto detectado:")
    st.text(texto_ocr)

    datos = extraer_datos_ocr(texto_ocr)
    st.subheader("📌 Datos extraídos:")
    for campo, valor in datos.items():
        st.write(f"**{campo}**: {valor if valor else 'No detectado'}")
