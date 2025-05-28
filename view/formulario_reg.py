import streamlit as st
import pymysql
import numpy as np
import cv2
from app.embedings import crear_embedding
from db.model_user import guardar_usuario

def mostrar_formulario():
    st.markdown("---")
    st.markdown('<h3><i class="bi bi-person-fill"></i> Formulario de Registro</h3>', unsafe_allow_html=True)
    
    if "embedding" not in st.session_state:
        st.session_state.embedding = None
    if "imagen" not in st.session_state:
        st.session_state.imagen = None

    # Selección dinámica
    facultad = st.selectbox("Facultad", ["Ingeniería", "Ciencias Sociales", "Educación"])

    if facultad == "Ingeniería":
        carreras = ["Sistemas", "Civil", "Industrial"]
    elif facultad == "Ciencias Sociales":
        carreras = ["Derecho", "Psicología", "Comunicación"]
    elif facultad == "Educación":
        carreras = ["Inicial", "Primaria", "Secundaria"]
    else:
        carreras = []

    carrera = st.selectbox("Carrera", carreras)

    with st.form("form_registro"):
        nombre = st.text_input("Nombre completo")
        codigo = st.text_input("Código estudiantil")
        
        img_file = st.camera_input("📸 Captura tu rostro")

        registrar = st.form_submit_button("✅ Registrar estudiante")

        if registrar:
            if img_file is None:
                st.error("❌ Primero debes capturar el rostro.")
            elif not (nombre and codigo):
                st.warning("⚠️ Completa todos los campos.")
            else:
                # Procesar imagen capturada
                file_bytes = np.asarray(bytearray(img_file.getvalue()), dtype=np.uint8)
                frame = cv2.imdecode(file_bytes, 1)

                embedding = crear_embedding(frame)

                if embedding is None:
                    st.error("❌ No se detectó rostro.")
                else:
                    try:
                        guardar_usuario(nombre, codigo, facultad, carrera, embedding)
                        st.success(f"✅ Usuario {nombre} registrado correctamente.")
                        st.session_state.embedding = None
                        st.session_state.imagen = None
                    except pymysql.err.IntegrityError:
                        st.error(f"❌ El código '{codigo}' ya está registrado. Usa uno diferente.")
