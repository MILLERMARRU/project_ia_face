import streamlit as st
import cv2, numpy as np
from app.embedings import crear_embedding
from app.verificacion_faiss import construir_indice, buscar_usuario_por_embedding

def verificar_usuario():
    st.subheader("🔍 Verificación de Identidad")

    # --- Ajustes de FAISS ---
    modo_ui = st.radio(
        "Selecciona el modo de verificación:",
        ("Mayor velocidad", "Mayor precisión"),
        horizontal=True
    )
    modo_faiss = "speed" if modo_ui == "Mayor velocidad" else "accuracy"
    st.info(
        "El modo de **Mayor velocidad** usa embeddings promediados, mientras que **Mayor precisión** usa todos los embeddings individuales."
    )

    # --- Captura de imagen ---
    img_file = st.camera_input("📸 Captura tu rostro y pulsa «Usar foto»", key="unique_camera_input")

    if img_file is None:
        st.info("Cuando estés listo toma la foto.")
        st.stop()

    # Procesar la imagen subida en OpenCV BGR
    frame = cv2.imdecode(
        np.frombuffer(img_file.getvalue(), dtype=np.uint8), 
        cv2.IMREAD_COLOR
    )

    with st.spinner("Generando embedding y consultando el índice…"):
        emb = crear_embedding(frame)

        if emb is None:
            st.warning("❌ No se detectó ningún rostro. Prueba de nuevo.")
            st.stop()

        # Construir o cargar índice según el modo
        construir_indice(modo=modo_faiss)
        usuario, similitud = buscar_usuario_por_embedding(emb)

    # --- Resultado ---
    if usuario:
        st.success(f"🎉 Usuario identificado: {usuario['nombre']}")
        st.markdown(
            f"""
            - **Código:** `{usuario['codigo']}`  
            - **Facultad:** {usuario['facultad']}  
            - **Carrera:** {usuario['carrera']}  
            - **Similitud:** `{similitud:.4f}`
            """
        )
    else:
        st.error("❌ Usuario no identificado.")
        st.info(f"Similitud máxima encontrada: {similitud:.4f}")
