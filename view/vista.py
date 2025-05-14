import streamlit as st
from view.formulario_reg import mostrar_formulario
from view.verificacion_usuario import verificar_usuario

def vista_inicio():
    st.markdown("""
        <div style='text-align: center;'>
            <h1>🎓 Sistema de Registro Estudiantil  UCSS</h1>
            <h3>Prototipo v1.0.0</h3>
            <hr style='border:1px solid #ccc'>
            <p>Bienvenido al sistema de asistencia mediante reconocimiento facial.</p>
        </div>
    """, unsafe_allow_html=True)

    # Estados de sesión para control de vistas
    if "mostrar_formulario" not in st.session_state:
        st.session_state.mostrar_formulario = False
    if "verificar_usuario" not in st.session_state:
        st.session_state.verificar_usuario = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Registrar estudiante"):
            st.session_state.mostrar_formulario = True
            st.session_state.verificar_usuario = False  # ← desactiva otra vista
    with col2:
        if st.button("✅ Comprobar registro"):
            st.session_state.verificar_usuario = True
            st.session_state.mostrar_formulario = False

    # Mostrar formulario o verificación según el estado
    if st.session_state.mostrar_formulario:
        mostrar_formulario()
    elif st.session_state.verificar_usuario:
        verificar_usuario()
