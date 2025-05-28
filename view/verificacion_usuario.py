import streamlit as st
import cv2
import numpy as np
from app.embedings import crear_embedding
from app.verificacion_faiss import construir_indice, buscar_usuario_por_embedding

def verificar_usuario():
    st.subheader("🔍 Verificación de Identidad")

    img_file = st.camera_input("📸 Captura tu rostro para verificar")

    if img_file is not None:
        # Leer la imagen de la cámara en formato OpenCV
        file_bytes = np.asarray(bytearray(img_file.getvalue()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)  # 1 = color

        try:
            st.success("✅ Imagen capturada. Generando embedding...")
            embedding = crear_embedding(frame)

            construir_indice()
            usuario, similitud = buscar_usuario_por_embedding(embedding)

            if usuario:
                st.success(f"🎉 Usuario identificado: {usuario['nombre']}")
                st.write(f"Código: `{usuario['codigo']}`")
                st.write(f"Facultad: {usuario['facultad']}")
                st.write(f"Carrera: {usuario['carrera']}")
                st.write(f"🔎 Similitud: `{similitud:.4f}`")
            else:
                st.error("❌ Usuario no identificado. Prueba nuevamente.")
                st.info(f"Similitud máxima encontrada: {similitud:.4f}")

        except Exception as e:
            st.error(f"❌ Error al verificar rostro: {str(e)}")