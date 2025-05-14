import streamlit as st
import pymysql
from app.camara import capturar_rostro
from app.embedings import crear_embedding
from db.model_user import guardar_usuario

def mostrar_formulario():
    st.markdown("---")
    st.subheader("📋 Formulario de Registro")

    if "embedding" not in st.session_state:
        st.session_state.embedding = None
    if "imagen" not in st.session_state:
        st.session_state.imagen = None

    # Selección dinámica fuera del formulario
    facultad = st.selectbox("Facultad", ["Ingeniería", "Ciencias Sociales", "Educación"])

    if facultad == "Ingeniería":
        carreras = ["Chistemas", "Civil", "Industrial"]
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

        col1, col2 = st.columns(2)
        with col1:
            capturar = st.form_submit_button("📸 Capturar rostro")
        with col2:
            registrar = st.form_submit_button("✅ Registrar estudiante")

        if capturar:
            imagen = capturar_rostro()
            if imagen is not None:
                embedding = crear_embedding(imagen)
                if embedding is not None:
                    st.session_state.embedding = embedding
                    st.session_state.imagen = imagen
                    st.success("✅ Rostro capturado y embedding generado.")
                else:
                    st.error("❌ No se detectó rostro.")
            else:
                st.warning("⚠️ No se capturó imagen.")

        if registrar:
            if st.session_state.embedding is None:
                st.error("❌ Primero debes capturar el rostro.")
            elif not (nombre and codigo):
                st.warning("⚠️ Completa todos los campos.")
            else:
                try:
                    guardar_usuario(nombre, codigo, facultad, carrera, st.session_state.embedding)
                    st.success(f"✅ Usuario {nombre} registrado correctamente.")
                    st.session_state.embedding = None
                    st.session_state.imagen = None
                except pymysql.err.IntegrityError:
                    st.error(f"❌ El código '{codigo}' ya está registrado. Usa uno diferente.")
