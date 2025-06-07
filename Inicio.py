import streamlit as st
import functions as f
from datetime import date

# --- Page Configuration (Optional but Recommended) ---
st.set_page_config(
    page_title="InfoMed - Login",
    page_icon="🏥",
    layout="centered" # "wide" or "centered"
)

# --- Main Application ---
st.title("¡Bienvenido a InfoMed!")

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
    st.markdown(
    """
    <h1 style='font-size: 36px; color: 	#3187d0; text-align: center;'>
        Tu bienestar es nuestra prioridad
    </h1>
    </br>
    """,
    unsafe_allow_html=True
)

# Pantalla de inicio
if st.session_state.pantalla is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Iniciar sesión", use_container_width=True):
            st.session_state.pantalla = "login"
            st.rerun()  # ✅ nueva forma de forzar recarga
    with col2:
        if st.button("📝 Registrarse", use_container_width=True):
            st.session_state.pantalla = "seleccion_tipo"
            st.rerun()

# Selección tipo de registro
elif st.session_state.pantalla == "seleccion_tipo":
    st.subheader("¿Cómo querés registrarte?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👨‍⚕️ Médico", use_container_width=True):
            st.session_state.tipo_usuario = "medico"
            st.session_state.pantalla = "registro"
            st.rerun()
    with col2:
        if st.button("🧑‍🦱 Paciente", use_container_width=True):
            st.session_state.tipo_usuario = "paciente"
            st.session_state.pantalla = "registro"
            st.rerun()

# Registro
elif st.session_state.pantalla == "registro":
    tipo = st.session_state.tipo_usuario
    st.subheader(f"Registro como {'Médico' if tipo == 'medico' else 'Paciente'}")

    dni = st.text_input("🆔 DNI")
    nombre = st.text_input("👤 Nombre")
    apellido = st.text_input("👤 Apellido")
   
    
    sexo = st.selectbox("⚧ Sexo", ["M", "F", "O"])

    if tipo == "medico":
        telefono = st.text_input("📞 Teléfono")
        correo = st.text_input("📧 Correo electrónico")
        contraseña = st.text_input("🔑 Contraseña", type="password")
    elif tipo == "paciente":
        fecha_de_nacimiento = st.date_input("📅 Fecha de nacimiento")
        direccion = st.text_input("🏠 Dirección")
        codigo_postal = st.text_input("📬 Código postal")
        obra_social = st.text_input("🏥 Obra social")
        correo = st.text_input("📧 Correo electrónico")
        contraseña = st.text_input("🔑 Contraseña", type="password")
    
    if st.button("✅ Registrarme"):
        tipo = st.session_state.tipo_usuario
        if tipo == "paciente":
            # Validar que todos los campos estén completos para paciente
            if dni and apellido and nombre and fecha_de_nacimiento and sexo and direccion and codigo_postal and obra_social and correo and contraseña:
                resultado = f.registrar_usuario(
                    dni=dni,
                    apellido=apellido,
                    nombre=nombre,
                    fecha_de_nacimiento=fecha_de_nacimiento,
                    sexo=sexo,
                    direccion=direccion,
                    codigo_postal=codigo_postal,
                    obra_social=obra_social,
                    correo=correo,
                    contraseña=contraseña
                )
                if resultado:
                    st.success("✅ Paciente registrado con éxito.")
                    # Opcional: redirigir a login después del registro exitoso
                    # st.session_state.pantalla = "login"
                    # st.rerun()
                else:
                    st.error("❌ Hubo un error al registrar el paciente.")
            else:
                st.warning("⚠️ Completá todos los campos antes de continuar.")
                st.write("**Campos faltantes:**")
                if not dni: st.write("- DNI")
                if not apellido: st.write("- Apellido")
                if not nombre: st.write("- Nombre")
                if not sexo: st.write("- Sexo")
                if not direccion: st.write("- Dirección")
                if not codigo_postal: st.write("- Código postal")
                if not obra_social: st.write("- Obra social")
                if not correo: st.write("- Correo electrónico")
                if not contraseña: st.write("- Contraseña")
        elif tipo == "medico":
            # Validar que todos los campos estén completos para medico
            if dni and apellido and nombre and sexo and telefono and correo and contraseña:
                resultado = f.registrar_medico(
                    dni=dni,
                    apellido=apellido,
                    nombre=nombre,
                    sexo=sexo,
                    telefono=telefono,
                    correo=correo,
                    contraseña=contraseña
                )
                if resultado:
                    st.success("✅ Médico registrado con éxito.")
                    # Opcional: redirigir a login después del registro exitoso
                    # st.session_state.pantalla = "login"
                    # st.rerun()
                else:
                    st.error("❌ Hubo un error al registrar el médico.")
            else:
                st.warning("⚠️ Completá todos los campos antes de continuar.")
                st.write("**Campos faltantes:**")
                if not dni: st.write("- DNI")
                if not apellido: st.write("- Apellido")
                if not nombre: st.write("- Nombre")
                if not sexo: st.write("- Sexo")
                if not telefono: st.write("- Teléfono")
                if not correo: st.write("- Correo electrónico")
                if not contraseña: st.write("- Contraseña")