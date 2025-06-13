# asistencia_tiempo_real.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av, cv2, numpy as np, pandas as pd
from datetime import datetime
import uuid, os, io   # noqa

from app.embeddings_multiples import crear_embeddings_multiples
from app.verificacion_faiss import construir_indice, buscar_usuario_por_embedding

# ---------- CONFIGURACIÓN GLOBAL ----------
FRAME_STRIDE = 3          # procesa 1 de cada 3 frames
SIM_COLOR = [(0.35, (0,0,255)),  # rojo: similitud < 0.35
             (0.50, (0,255,255)),# ámbar: 0.35-0.49
             (1.01,(0,255,0))]   # verde: ≥0.50

# Guardaremos el índice FAISS y su modo en cache de Streamlit
if "faiss_mode" not in st.session_state:
    st.session_state.faiss_mode = None
if "faiss_index_ready" not in st.session_state:
    st.session_state.faiss_index_ready = False
if "asistencia" not in st.session_state:
    st.session_state.asistencia = {}          # dict {codigo: datos}
if "webrtc_key" not in st.session_state:
    st.session_state.webrtc_key = f"asist_{uuid.uuid4()}"

# ---------- CONSTRUCTOR DEL ÍNDICE SEGÚN MODO ----------
def ensure_faiss(mode: str):
    if (not st.session_state.faiss_index_ready) or (mode != st.session_state.faiss_mode):
        construir_indice(modo=mode)
        st.session_state.faiss_index_ready = True
        st.session_state.faiss_mode = mode
        st.toast(f"Índice FAISS ({mode}) listo", icon="✅")

# ---------- PROCESADOR DE VÍDEO ----------
class Reconocedor(VideoProcessorBase):
    def __init__(self, mode: str):
        super().__init__()
        self.mode = mode
        self.frame_idx = 0

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        self.frame_idx += 1

        # Procesamos solo cada FRAME_STRIDE-ésimo frame
        if self.frame_idx % FRAME_STRIDE != 0:
            return frame

        caras = crear_embeddings_multiples(img)
        for cara in caras:
            emb = cara.embedding
            x1, y1, x2, y2 = cara.bbox.astype(int)

            usuario, sim = buscar_usuario_por_embedding(emb)
            if usuario:
                # --- Registro en sesión (sin duplicados) ---
                codigo = usuario["codigo"]
                if codigo not in st.session_state.asistencia:
                    st.session_state.asistencia[codigo] = {
                        "Nombre": usuario["nombre"],
                        "Código": codigo,
                        "Facultad": usuario["facultad"],
                        "Carrera": usuario["carrera"],
                        "Similitud": round(sim, 4),
                        "FechaHora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                texto = f"{usuario['nombre']} ({sim:.2f})"
            else:
                texto = "Desconocido"
                sim = 0.0

            # --- Color dinámico por similitud ---
            for thr, col in SIM_COLOR:
                if sim < thr:
                    color = col
                    break

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, texto, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# ---------- VISTA STREAMLIT ----------
def vista_asistencia_tiempo_real():
    st.title("📡 Asistencia en tiempo real")

    # --- Modo de búsqueda Speed / Accuracy ----
    mode_ui = st.radio(
        "Modo de búsqueda:",
        ("speed", "accuracy"), horizontal=True, index=0
    )
    ensure_faiss(mode_ui)

    # --- Lanza WebRTC ---
    webrtc_streamer(
        key=st.session_state.webrtc_key,
        video_processor_factory=lambda: Reconocedor(mode_ui),
        async_processing=True,
        media_stream_constraints={"video": {"width": 640, "height": 480}, "audio": False},
    )

    # --- Tabla de asistencias ----
    if st.session_state.asistencia:
        st.markdown("### 🧾 Asistencias registradas")
        df = pd.DataFrame.from_dict(st.session_state.asistencia, orient="index")
        st.dataframe(df, use_container_width=True)

        # Botón para descargar una sola vez
        buffer = io.BytesIO()
        if st.download_button(
            "📥 Descargar Excel",
            data=(lambda _df=df, _io=buffer: (
                _df.to_excel(_io, index=False, sheet_name="Asistencia"), _io.seek(0), _io.read()
            ))()[2],
            file_name=f"ASISTENCIA_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            st.toast("Excel generado ✅", icon="📄")

    # --- Limpieza ---
    if st.button("🧹 Reiniciar lista"):
        st.session_state.asistencia.clear()
        st.rerun()
