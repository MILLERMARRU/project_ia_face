
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import numpy as np
import pandas as pd
import io
import os
import uuid
from datetime import datetime

from app.embeddings_multiples import crear_embeddings_multiples
from app.verificacion_faiss import construir_indice, buscar_usuario_por_embedding
from app import asistencia_global


# === CLASE TRANSFORMADOR EN TIEMPO REAL ===
class Reconocedor(VideoTransformerBase):
    def __init__(self):
        self.ya_registrados = set()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        faces = crear_embeddings_multiples(img)

        for face in faces:
            emb = face.embedding
            x1, y1, x2, y2 = face.bbox.astype(int)

            usuario, similitud = buscar_usuario_por_embedding(emb)

            if usuario:
                color = (0, 255, 0)  # Verde para identificados
                texto = f"{usuario['nombre']}"

                if usuario["codigo"] not in self.ya_registrados:
                    self.ya_registrados.add(usuario["codigo"])

                    ya_existe = any(u["Código"] == usuario["codigo"] for u in asistencia_global.asistencias_temp)
                    if not ya_existe:
                        asistencia_global.asistencias_temp.append({
                            "Nombre": usuario["nombre"],
                            "Código": usuario["codigo"],
                            "Facultad": usuario["facultad"],
                            "Carrera": usuario["carrera"],
                            "Similitud": round(similitud, 4),
                            "Fecha y hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.session_state.asistencia_finalizada = True

            else:
                color = (0, 0, 255)  # Rojo para no identificados
                texto = "Desconocido"

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, texto, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# === GUARDAR AUTOMÁTICAMENTE EN DISCO LOCAL ===
def guardar_backup_excel(df):
    ahora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    carpeta = "asistencias"
    try:
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"ASISTENCIA_{ahora}.xlsx")
        df.to_excel(ruta, index=False, sheet_name="Asistencia")

        # Leer contenido para descarga
        with open(ruta, "rb") as f:
            contenido = f.read()

        return ruta, contenido  # <-- NUEVO

    except Exception as e:
        st.warning(f"⚠️ No se pudo guardar en disco: {e}")
        return None, None



# === VISTA PRINCIPAL DE ASISTENCIA ===
def vista_asistencia_tiempo_real():
    st.title("📡Asistencia en Tiempo Real ")

    if "asistencia" not in st.session_state:
        st.session_state.asistencia = []
    if "asistencia_finalizada" not in st.session_state:
        st.session_state.asistencia_finalizada = False
    if "faiss_cargado" not in st.session_state:
        construir_indice()
        st.session_state.faiss_cargado = True
        st.success("✅ Índice FAISS cargado")

    # Generar key único para evitar errores
    if "webrtc_key" not in st.session_state:
        st.session_state.webrtc_key = f"asistencia_{uuid.uuid4()}"

    webrtc_streamer(
        key=st.session_state.webrtc_key,
        video_transformer_factory=Reconocedor,
        media_stream_constraints={"video": {"width": 640, "height": 480}, "audio": False},
        rtc_configuration={
            "iceServers": [
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "turn:turn.example.com:3478", "username": "user", "credential": "pass"}
            ]
        },
        async_transform=True
    )

    # Solo actualizar si hay datos nuevos
    if asistencia_global.asistencias_temp:
        st.session_state.asistencia = asistencia_global.asistencias_temp.copy()
        st.session_state.asistencia_finalizada = True
        asistencia_global.asistencias_temp.clear()  # Limpia luego de usar

    # Mostrar asistencia si ya se registró
    if  st.session_state.asistencia_finalizada and st.session_state.asistencia:
        st.markdown("---")
        st.markdown("### 🧾 Asistencias registradas:")
        df = pd.DataFrame(st.session_state.asistencia)     

        st.dataframe(df)

        # Guardar localmente
        # Guardar una sola vez y obtener el contenido
        ruta, contenido = guardar_backup_excel(df)
        if ruta:
            st.success(f"📁 Backup guardado en: `{ruta}`")

            # Botón de descarga usando el mismo archivo
            st.download_button(
                "📥 Descargar Excel",
                data=contenido,
                file_name=os.path.basename(ruta),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # === 🧹 LIMPIEZA OPCIONAL ===
        if st.button("🧹 Limpiar y reiniciar asistencia"):
            st.session_state.asistencia = []
            st.session_state.asistencia_finalizada = False
            st.rerun()