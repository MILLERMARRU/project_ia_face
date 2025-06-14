
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
    if "modo_reconocimiento" not in st.session_state:
        st.session_state.modo_reconocimiento = "speed"
    if "faiss_cargado" not in st.session_state:
        st.session_state.faiss_cargado = False

    # === SELECTOR DE MODO DE RECONOCIMIENTO ===
    st.markdown("### ⚙️ Configuración de Reconocimiento")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        modo_anterior = st.session_state.modo_reconocimiento
        modo_nuevo = st.selectbox(
            "Selecciona el modo de reconocimiento:",
            options=["speed", "accuracy"],
            format_func=lambda x: "🚀 Velocidad (promedio de embeddings)" if x == "speed" 
                                 else "🎯 Precisión (embeddings individuales)",
            index=0 if st.session_state.modo_reconocimiento == "speed" else 1,
            key="selector_modo"
        )
          # Si cambió el modo, actualizar y recargar índice
        if modo_nuevo != modo_anterior:
            st.session_state.modo_reconocimiento = modo_nuevo
            st.session_state.faiss_cargado = False
    
    with col2:
        if st.button("🔄 Recargar Índice"):
            st.session_state.faiss_cargado = False    # Cargar o recargar índice según el modo seleccionado
    if not st.session_state.faiss_cargado:
        with st.spinner(f"🔄 Cargando índice en modo {st.session_state.modo_reconocimiento}..."):
            try:
                construir_indice(modo=st.session_state.modo_reconocimiento)
                st.session_state.faiss_cargado = True
                
                modo_texto = "🚀 Velocidad (embeddings promedio)" if st.session_state.modo_reconocimiento == "speed" else "🎯 Precisión (embeddings individuales)"
                st.success(f"✅ Índice FAISS cargado en modo: {modo_texto}")
                
                # Mostrar información adicional sobre el modo y estadísticas
                from app.verificacion_faiss import index, usuarios_indexados
                num_vectores = index.ntotal
                num_usuarios = len(set(u.get('codigo', u.get('idUser', 'unknown')) for u in usuarios_indexados))
                
                if st.session_state.modo_reconocimiento == "speed":
                    st.info(f"ℹ️ Modo Velocidad: {num_vectores} embeddings promedio de {num_usuarios} usuarios (más rápido)")
                else:
                    st.info(f"ℹ️ Modo Precisión: {num_vectores} embeddings individuales de {num_usuarios} usuarios (más preciso)")
                    
            except Exception as e:
                st.error(f"❌ Error al cargar índice: {e}")
                st.session_state.faiss_cargado = False

    st.markdown("---")

    # === INDICADOR DEL MODO ACTIVO ===
    if st.session_state.faiss_cargado:
        if st.session_state.modo_reconocimiento == "speed":
            st.info("🚀 **MODO ACTIVO: VELOCIDAD** - Usando embeddings promedio para reconocimiento rápido")
        else:
            st.info("🎯 **MODO ACTIVO: PRECISIÓN** - Usando embeddings individuales para mayor precisión")

    # === CÁMARA EN TIEMPO REAL ===
    st.markdown("### 📹 Reconocimiento Facial en Tiempo Real")
    
    # Generar key único para evitar errores
    if "webrtc_key" not in st.session_state:
        st.session_state.webrtc_key = f"asistencia_{uuid.uuid4()}"

    webrtc_streamer(
        key=st.session_state.webrtc_key,
        video_transformer_factory=Reconocedor,
        media_stream_constraints={"video": {"width": 640, "height": 480}, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        async_transform=True
    )

    # Solo actualizar si hay datos nuevos
    if asistencia_global.asistencias_temp:
        st.session_state.asistencia = asistencia_global.asistencias_temp.copy()
        st.session_state.asistencia_finalizada = True
        asistencia_global.asistencias_temp.clear()  # Limpia luego de usar    # Mostrar asistencia si ya se registró
    if st.session_state.asistencia_finalizada and st.session_state.asistencia:
        st.markdown("---")
        st.markdown("### 🧾 Asistencias registradas:")
        df = pd.DataFrame(st.session_state.asistencia)

        st.write("✅ Asistencias detectadas:", len(st.session_state.asistencia))
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