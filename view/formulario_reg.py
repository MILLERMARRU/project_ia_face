import streamlit as st
import numpy as np
import pymysql
import cv2

from app.embedings import crear_embedding
from db.model_user import guardar_usuario

NUM_CAPTURAS = 4
MENSAJES = [
    "Intenta una expresión facial diferente 😊",
    "Cambia ligeramente el ángulo de tu rostro ↗️",
    "Prueba con otra iluminación 💡",
    "Aléjate o acércate un poco 📏"
]

def init_session():
    for k, v in {
        "img_list": [],
        "emb_list": [],
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

def procesar_camara(uploaded_file):
    """Convierte el archivo de st.camera_input a np.ndarray BGR."""
    img_bytes = uploaded_file.getvalue()
    frame = cv2.imdecode(
        np.frombuffer(img_bytes, dtype=np.uint8), 
        cv2.IMREAD_COLOR
    )
    return frame

def mostrar_formulario():
    init_session()

    st.markdown("---")
    st.markdown('<h3><i class="bi bi-person-fill"></i> Registro de Estudiante</h3>', unsafe_allow_html=True)

    # --------- Campos de selección (fuera del form) ----------
    facultad = st.selectbox("Facultad", ["Ingeniería", "Ciencias Sociales", "Educación"])
    carreras = {
        "Ingeniería": ["Sistemas", "Civil", "Industrial"],
        "Ciencias Sociales": ["Derecho", "Psicología", "Comunicación"],
        "Educación": ["Inicial", "Primaria", "Secundaria"],
    }[facultad]
    carrera = st.selectbox("Carrera", carreras)

    # --------- Formulario principal ----------
    with st.form("form_registro", clear_on_submit=False):
        nombre = st.text_input("Nombre completo", placeholder="Ej.: Andrea Rojas")
        codigo = st.text_input("Código estudiantil")

        # --- Zona de captura múltiple ---
        st.write(f"Capturas realizadas: **{len(st.session_state.img_list)}/{NUM_CAPTURAS}**")
        cam_file = st.camera_input("📸 Toma una foto")

        col1, col2, col3 = st.columns(3)
        capturar = col1.form_submit_button("➕ Guardar captura")
        borrar    = col2.form_submit_button("♻️ Reiniciar capturas")
        registrar = col3.form_submit_button("✅ Registrar estudiante")

        # --- Acciones ---
        if capturar:
            if cam_file is None:
                st.warning("Primero toma una foto.")
            elif len(st.session_state.img_list) >= NUM_CAPTURAS:
                st.info("Ya alcanzaste el número máximo de capturas.")
            else:
                frame = procesar_camara(cam_file)
                with st.spinner("Procesando..."):
                    emb = crear_embedding(frame)

                if emb is None:
                    st.error("❌ No se detectó rostro. Vuelve a intentar.")
                else:
                    st.session_state.img_list.append(frame)
                    st.session_state.emb_list.append(emb)
                    idx = len(st.session_state.img_list)
                    st.success(f"Captura {idx} almacenada. {MENSAJES[(idx-1)%len(MENSAJES)]}")

        if borrar:
            st.session_state.img_list.clear()
            st.session_state.emb_list.clear()
            st.info("Capturas reiniciadas.")

        # Mostrar miniaturas
        if st.session_state.img_list:
            st.image(
                st.session_state.img_list, 
                width=120, 
                caption=[f"Captura {i+1}" for i in range(len(st.session_state.img_list))]
            )

        # --- Registro final ---
        if registrar:
            # Validaciones
            if len(st.session_state.img_list) < NUM_CAPTURAS:
                st.error(f"Faltan capturas. Necesitas {NUM_CAPTURAS}.")
            elif not (nombre and codigo):
                st.warning("Completa nombre y código.")
            else:
                try:
                    # ➜ Guarda la **lista** de embeddings
                    guardar_usuario(
                        nombre, codigo, facultad, carrera, st.session_state.emb_list
                    )
                    st.success(f"Usuario «{nombre}» registrado correctamente ✅")
                    # Limpieza de sesión
                    st.session_state.img_list.clear()
                    st.session_state.emb_list.clear()
                except pymysql.err.IntegrityError:
                    st.error(f"El código «{codigo}» ya existe. Usa otro.")
