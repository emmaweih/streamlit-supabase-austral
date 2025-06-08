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

# Estados adicionales para manejar la lógica del hospital
if "hospital_verificado" not in st.session_state:
    st.session_state.hospital_verificado = False
if "hospital_existe" not in st.session_state:
    st.session_state.hospital_existe = None
if "datos_hospital_temp" not in st.session_state:
    st.session_state.datos_hospital_temp = {}
if "mostrar_campos_hospital" not in st.session_state:
    st.session_state.mostrar_campos_hospital = False

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
        
        st.markdown("---")
        st.subheader("🏥 Información del Hospital")
        
        # Campo para el nombre del hospital
        col1, col2 = st.columns([3, 1])
        with col1:
            hospital = st.text_input("Nombre del Hospital", 
                                   value=st.session_state.datos_hospital_temp.get('nombre', ''))
        
        
            if st.button("🔍 Verificar", disabled=not hospital):
                if hospital:
                    # Buscar el hospital en la base de datos
                    hospital_encontrado = f.buscar_hospital_por_nombre(hospital)
                    
                    if hospital_encontrado:
                        st.session_state.hospital_existe = True
                        st.session_state.hospital_verificado = True
                        st.session_state.mostrar_campos_hospital = False
                        st.session_state.datos_hospital_temp = {
                            'nombre': hospital,
                            'datos_existente': hospital_encontrado
                        }
                        st.success(f"✅ Hospital encontrado: {hospital_encontrado['desc_hospital']}")
                        st.info(f"📍 {hospital_encontrado['direccion']}")
                        st.info(f"📞 {hospital_encontrado['telefono']}")

                    else:
                        st.session_state.hospital_existe = False
                        st.session_state.hospital_verificado = True
                        st.session_state.mostrar_campos_hospital = True
                        st.session_state.datos_hospital_temp['nombre'] = hospital
                        st.warning("⚠️ Hospital no encontrado. Por favor, ingresa los datos del hospital.")
                        st.rerun()
        

        
        # Campos adicionales si el hospital no existe
        direccion_hospital = None
        telefono_hospital = None
        
        if st.session_state.mostrar_campos_hospital:
            st.markdown("### Datos del Nuevo Hospital")
            direccion_hospital = st.text_input("📍 Dirección del Hospital", 
                                             value=st.session_state.datos_hospital_temp.get('direccion', ''))
            telefono_hospital = st.text_input("📞 Teléfono del Hospital", 
                                            value=st.session_state.datos_hospital_temp.get('telefono', ''))
            
            # Guardar datos temporalmente
            st.session_state.datos_hospital_temp.update({
                'direccion': direccion_hospital,
                'telefono': telefono_hospital
            })
        
        # Opcional: Mostrar hospitales existentes como ayuda
        with st.expander("Ver hospitales registrados"):
            hospitales_existentes = f.obtener_hospitales_existentes()
            if hospitales_existentes:
                st.info("**Hospitales ya registrados:**")
                for hosp in hospitales_existentes:
                    st.write(f"• **{hosp['desc_hospital']}** - {hosp['direccion']}")
            else:
                st.info("No hay hospitales registrados aún.")
        

               
            
        
    elif tipo == "paciente":
        fecha_de_nacimiento = st.date_input("📅 Fecha de nacimiento")
        direccion = st.text_input("🏠 Dirección")
        codigo_postal = st.text_input("📬 Código postal")
        obra_social = st.text_input("🏥 Obra social")
        correo = st.text_input("📧 Correo electrónico")
        contraseña = st.text_input("🔑 Contraseña", type="password")
    
    # Botón de registro
    if st.button("✅ Registrarme"):
        tipo = st.session_state.tipo_usuario
        
        if tipo == "paciente":
            # Lógica para paciente (sin cambios)
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
                else:
                    st.error("❌ Hubo un error al registrar el paciente.")
            else:
                st.warning("⚠️ Completá todos los campos antes de continuar.")
                
        elif tipo == "medico":
            # Validación completa para médico
            campos_basicos_completos = dni and apellido and nombre and sexo and telefono and correo and contraseña and hospital
            hospital_verificado_ok = st.session_state.hospital_verificado
            
            # Si el hospital no existe, validar que se hayan ingresado los datos adicionales
            datos_hospital_completos = True
            if st.session_state.mostrar_campos_hospital:
                datos_hospital_completos = direccion_hospital and telefono_hospital
            
            if campos_basicos_completos and hospital_verificado_ok and datos_hospital_completos:
                # Proceder con el registro
                resultado = f.registrar_medico_con_hospital(
                    dni=dni,
                    apellido=apellido,
                    nombre=nombre,
                    sexo=sexo,
                    nombre_hospital=hospital,
                    direccion_hospital=direccion_hospital,
                    telefono_hospital=telefono_hospital,
                    telefono_medico=telefono,
                    correo=correo,
                    contraseña=contraseña
                )
                
                if resultado['success']:
                    st.success("✅ Médico registrado con éxito.")
                    
                    
                    # Limpiar estados temporales después del registro exitoso
                    st.session_state.hospital_verificado = False
                    st.session_state.hospital_existe = None
                    st.session_state.datos_hospital_temp = {}
                    st.session_state.mostrar_campos_hospital = False
                    
                else:
                    st.error(f"❌ Error al registrar el médico: {resultado.get('mensaje', 'Error desconocido')}")
            else:
                st.warning("⚠️ Completá todos los campos antes de continuar.")
                
                # Mostrar campos faltantes específicos
                st.write("**Verificá lo siguiente:**")
                if not campos_basicos_completos:
                    if not dni: st.write("- DNI")
                    if not apellido: st.write("- Apellido")
                    if not nombre: st.write("- Nombre")
                    if not sexo: st.write("- Sexo")
                    if not telefono: st.write("- Teléfono")
                    if not correo: st.write("- Correo electrónico")
                    if not contraseña: st.write("- Contraseña")
                    if not hospital: st.write("- Hospital")
                
                if not hospital_verificado_ok:
                    st.write("- Verificar el hospital usando el botón 🔍")
                
                if st.session_state.mostrar_campos_hospital and not datos_hospital_completos:
                    if not direccion_hospital: st.write("- Dirección del hospital")
                    if not telefono_hospital: st.write("- Teléfono del hospital")
    
    # Botón para volver
    if st.button("🔙 Volver"):
        # Limpiar estados temporales al volver
        st.session_state.hospital_verificado = False
        st.session_state.hospital_existe = None
        st.session_state.datos_hospital_temp = {}
        st.session_state.mostrar_campos_hospital = False
        st.session_state.pantalla = "seleccion_tipo"
        st.rerun()