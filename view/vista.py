import streamlit as st
from view.formulario_reg import mostrar_formulario
from view.verificacion_usuario import verificar_usuario
from view.asistencia_tiempo_real import vista_asistencia_tiempo_real
from streamlit_option_menu import option_menu

def vista_inicio():
    st.markdown("""
        <div style='text-align: center;'>
            <h1><i class="bi bi-bookmarks""></i> Sistema de Registro Estudiantil UCSS</h1>
            <h3>Prototipo v2.0.0</h3>
            <hr style='border:1px solid #ccc'>
            <p>Bienvenido al sistema de asistencia mediante reconocimiento facial.</p>
        </div>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    """, unsafe_allow_html=True)
     # Estados de sesión
    # Menú con iconos Bootstrap
    selected = option_menu(
        menu_title=None,
        options=["Registrar estudiante", "Comprobar registro", "Asistencia en tiempo real"],
        icons=["person-plus", "check2-circle", "graph-up"],
        orientation="horizontal"
    )


    if selected == "Registrar estudiante":
        mostrar_formulario()
    elif selected == "Comprobar registro":
        verificar_usuario()
    elif selected == "Asistencia en tiempo real":

        if "acceso_asistencia" not in st.session_state:
            st.session_state.acceso_asistencia = False

        if not st.session_state.acceso_asistencia:
            with st.form("form_password"):
                password = st.text_input("Ingrese la contraseña para acceder al módulo:", type="password")
                submit = st.form_submit_button("Entrar")
                if submit:
                    if password == "miller123":  
                        st.session_state.acceso_asistencia = True
                        st.success("Acceso concedido.")
                        st.rerun()
                    else:
                        st.error("Contraseña incorrecta.")
        else:
            vista_asistencia_tiempo_real()