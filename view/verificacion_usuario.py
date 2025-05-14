import streamlit as st
import cv2
from app.embedings import crear_embedding
from app.verificacion_faiss import construir_indice, buscar_usuario_por_embedding

def verificar_usuario():
    st.subheader("🔍 Verificación de Identidad")

    if st.button("📸 Capturar rostro para verificar"):
        cap = cv2.VideoCapture(0)
        st.info("Presiona 's' en la ventana emergente para capturar rostro")

        while True:
            ret, frame = cap.read()
            cv2.imshow("Presiona 's' para capturar", frame)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                break

        cap.release()
        cv2.destroyAllWindows()

        try:
            st.success("✅ Imagen capturada. Generando embedding...")
            embedding = crear_embedding(frame)

            # Construir el índice de FAISS
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
