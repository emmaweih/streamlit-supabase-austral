import streamlit as st

# --- Page Configuration (Optional but Recommended) ---
st.set_page_config(
    page_title="InfoMed - Login",
    page_icon="🏥",
    layout="centered" # "wide" or "centered"
)

# --- Main Application ---
st.title("InfoMed")

import streamlit as st

# Estilos
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #0077b6;
        text-align: center;
    }
    .subtitle {
        font-size: 20px;
        color: #023e8a;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Estado inicial
if "pantalla" not in st.session_state:
    st.session_state.pantalla = None
if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = None
if "nombre_usuario" not in st.session_state:
    st.session_state.nombre_usuario = "Usuario"

# Títulos generales
if st.session_state.pantalla != "perfil":
    st.markdown('<p class="title">🏥 Bienvenido a InfoMed</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Tu bienestar es nuestra prioridad</p>', unsafe_allow_html=True)

# Pantalla de inicio
if st.session_state.pantalla is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Iniciar sesión", use_container_width=True):
            st.session_state.pantalla = "login"
    with col2:
        if st.button("📝 Registrarse", use_container_width=True):
            st.session_state.pantalla = "seleccion_tipo"

# Selección tipo de registro
elif st.session_state.pantalla == "seleccion_tipo":
    st.subheader("¿Cómo querés registrarte?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👨‍⚕️ Médico", use_container_width=True):
            st.session_state.tipo_usuario = "medico"
            st.session_state.pantalla = "registro"
    with col2:
        if st.button("🧑‍🦱 Paciente", use_container_width=True):
            st.session_state.tipo_usuario = "paciente"
            st.session_state.pantalla = "registro"

# Registro
elif st.session_state.pantalla == "registro":
    tipo = st.session_state.tipo_usuario
    st.subheader(f"Registro como {'Médico' if tipo == 'medico' else 'Paciente'}")

    dni = st.text_input("🆔 DNI")
    apellido = st.text_input("👤 Apellido")
    nombre = st.text_input("👤 Nombre")
    fecha_nac = st.date_input("📅 Fecha de nacimiento")
    sexo = st.selectbox("⚧ Sexo", ["Masculino", "Femenino", "Otro"])

    if tipo == "medico":
        telefono = st.text_input("📞 Teléfono")
        correo = st.text_input("📧 Correo electrónico")
        contraseña = st.text_input("🔑 Contraseña", type="password")
    elif tipo == "paciente":
        direccion = st.text_input("🏠 Dirección")
        codigo_postal = st.text_input("📬 Código postal")
        obra_social = st.text_input("🏥 Obra social")
        correo = st.text_input("📧 Correo electrónico")
        contraseña = st.text_input("🔑 Contraseña", type="password")

    if st.button("✅ Registrarme"):
        if not dni or not nombre or not apellido or not correo or not contraseña:
            st.error("Por favor, completá todos los campos obligatorios.")
        else:
            st.session_state.nombre_usuario = nombre
            st.session_state.pantalla = "perfil"

# Login
elif st.session_state.pantalla == "login":
    st.subheader("Iniciar sesión")
    usuario = st.text_input("👤 Usuario")
    contraseña = st.text_input("🔑 Contraseña", type="password")

    if st.button("🔓 Entrar"):
        if usuario and contraseña:
            st.session_state.nombre_usuario = usuario
            # Por ahora asumimos que todos los que inician sesión son pacientes
            st.session_state.tipo_usuario = "paciente"
            st.session_state.pantalla = "perfil"
        else:
            st.error("Faltan datos.")

# Perfil post login/registro
elif st.session_state.pantalla == "perfil":
    nombre = st.session_state.nombre_usuario
    tipo = st.session_state.tipo_usuario

    st.markdown(f"## 👋 ¡Hola {nombre}!")
    if tipo == "medico":
        st.markdown("Estás en tu panel como **👨‍⚕️ Médico**.")
        st.write("Aquí podrías cargar pacientes, ver turnos, etc.")
    elif tipo == "paciente":
        st.markdown("Estás en tu panel como **🧑‍🦱 Paciente**.")
        st.write("Aquí podrías ver tu historial, pedir turnos, etc.")

    if st.button("Cerrar sesión"):
        st.session_state.clear()