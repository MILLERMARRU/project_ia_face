import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from insightface.app import FaceAnalysis

st.set_page_config(page_title="Detección de múltiples rostros", layout="centered")
st.title("📸 Detección de rostros (varias personas)")

# Inicializa InsightFace una sola vez con GPU
@st.cache_resource
def cargar_detector():
    app = FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    return app

app = cargar_detector()

# Captura desde cámara
foto = st.camera_input("Toma una foto con uno o más rostros")

if foto is not None:
    # Decodificar la imagen
    file_bytes = np.asarray(bytearray(foto.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # Convertir a RGB para InsightFace
    img_rgb = img[:, :, ::-1]

    # Detectar rostros
    faces = app.get(img_rgb)
    st.info(f"🔍 Rostros detectados: {len(faces)}")

    # Dibujar cuadros
    for face in faces:
        box = face.bbox.astype(int)
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

    # Mostrar imagen resultante
    img_rgb_draw = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    st.image(img_rgb_draw, caption="Resultado con rostros encuadrados", use_column_width=True)
