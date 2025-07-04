import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, date
import time
import sys
import re
import unicodedata
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase import create_client, Client

# Configuración de la página
st.set_page_config(
    page_title="InfoMed - Cargar Estudios",
    page_icon="🏥",
    layout="wide"
)

# Cargar variables de entorno
load_dotenv()

#solo médicos autenticados desde inicio
def solo_medico_autenticado():
    """
    Permite el acceso solo si el usuario está autenticado y es médico.
    Si no, muestra un mensaje y detiene la ejecución de la página.
    """
    if "usuario_autenticado" not in st.session_state or st.session_state.get("usuario_autenticado") is None:
        st.error("🔐 Debes iniciar sesión como médico para acceder a esta página")
        if st.button("🏠 Ir a la página principal"):
            st.switch_page("Inicio.py")
        st.stop()
    if st.session_state.get("tipo_usuario") != "medico":
        st.error("❌ Solo los médicos pueden acceder a esta página.")
        if st.button("🔙 Volver al perfil"):
            st.switch_page("Inicio.py")
        st.stop()


# Obtener el DNI del médico autenticado
medico_autenticado = st.session_state.get("usuario_autenticado")
if medico_autenticado is None:
    st.error("🔐 Debes iniciar sesión como médico para acceder a esta página")
    if st.button("🏠 Ir a la página principal"):
        st.switch_page("Inicio.py")
    st.stop()

# Verificar que el usuario sea un médico
if st.session_state.get("tipo_usuario") != "medico":
    st.error("❌ Solo los médicos pueden acceder a esta página.")
    if st.button("🔙 Volver al perfil"):
        st.switch_page("Inicio.py")
    st.stop()

DNI_MEDICO_AUTENTICADO = str(medico_autenticado.get('id_medico', ''))

# NUEVO: Configuración de Supabase Storage
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = "estudios"

def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def connect_to_supabase():
    """
    Connects to the Supabase PostgreSQL database using transaction pooler details
    and credentials stored in environment variables.
    """
    try:
        # Retrieve connection details from environment variables
        host = os.getenv("SUPABASE_DB_HOST")
        port = os.getenv("SUPABASE_DB_PORT")
        dbname = os.getenv("SUPABASE_DB_NAME")
        user = os.getenv("SUPABASE_DB_USER")
        password = os.getenv("SUPABASE_DB_PASSWORD")

        # Check if all required environment variables are set
        if not all([host, port, dbname, user, password]):
            st.error("Error: Una o más variables de entorno de Supabase no están configuradas.")
            st.error("Por favor configure: SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME, SUPABASE_DB_USER, y SUPABASE_DB_PASSWORD.")
            return None

        # Convert port to integer and establish the connection with SSL settings
        conn = psycopg2.connect(
            host=host,
            port=int(port),  # Convert port to integer - THIS IS CRITICAL
            dbname=dbname,
            user=user,
            password=password,
            sslmode='require',  # Add SSL mode for Supabase
            connect_timeout=10  # Add connection timeout
        )
        return conn
    except psycopg2.Error as e:
        st.error(f"Error conectando a la base de datos Supabase: {e}")
        return None

def execute_query(query, conn=None, params=None, is_select=True):
    """
    Executes a SQL query and returns the results as a pandas DataFrame for SELECT queries,
    or executes DML operations (INSERT, UPDATE, DELETE) and returns success status.
    """
    try:
        # Create a new connection if one wasn't provided
        close_conn = False
        if conn is None:
            conn = connect_to_supabase()
            if conn is None:
                return pd.DataFrame() if is_select else False
            close_conn = True
            
        # Create cursor and execute query
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if is_select:
            # Fetch all results for SELECT queries
            results = cursor.fetchall()
            
            # Get column names from cursor description
            colnames = [desc[0] for desc in cursor.description]
            
            # Create DataFrame
            df = pd.DataFrame(results, columns=colnames)
            result = df
        else:
            # For DML operations, commit changes and return success
            conn.commit()
            result = True
            
        # Close cursor and connection if we created it
        cursor.close()
        if close_conn:
            conn.close()
            
        return result
    except Exception as e:
        st.error(f"Error ejecutando consulta: {e}")
        # Rollback any changes if an error occurred during DML operation
        if conn and not is_select:
            conn.rollback()
        return pd.DataFrame() if is_select else False



# CSS personalizado para el estilo InfoMed
st.markdown("""
<style>
    .main-header {    
        text-align: center;
        background: linear-gradient(135deg, #63bdda 0%, #4a9bb8 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
        }
    .main-title {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: white;
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 0;
    }

    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        text-align: center;
        font-size: 1.1rem;
        margin: 1rem 0;
    }
    
    .confirmation-box {
        background: #fff3cd;
        color: #856404;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ffeaa7;
        text-align: center;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #f5c6cb;
        text-align: center;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: #4a90e2;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #357abd;
    }
    
    .patient-info {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #90caf9;
        margin: 1rem 0;
        text-align: center;
    }
    
    .dni-correction-form {
        background: #fff8e1;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ffb74d;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def buscar_paciente_por_dni(dni_paciente):
    """Busca un paciente por DNI y retorna sus datos"""
    try:
        query = "SELECT id_paciente, nombre, apellido, provincia, ciudad, calle, altura FROM paciente WHERE id_paciente = %s"
        df = execute_query(query, params=(dni_paciente,), is_select=True)
        
        if not df.empty:
            return {
                'id_paciente': int(df.iloc[0]['id_paciente']),
                'nombre': str(df.iloc[0]['nombre']),
                'apellido': str(df.iloc[0]['apellido']),
                'provincia': str(df.iloc[0]['provincia']),
                'ciudad': str(df.iloc[0]['ciudad']),
                'calle': str(df.iloc[0]['calle']),
                'altura': str(df.iloc[0]['altura'])
            }
        return None
    except Exception as e:
        st.error(f"Error buscando paciente: {e}")
        return None

def buscar_medico_por_dni(dni_medico):
    """Busca un médico por DNI y retorna sus datos incluyendo el sexo para determinar Dr/Dra y el hospital"""
    try:
        # MODIFICADO: Incluir el campo sexo y hospital en la consulta
        query = """
        SELECT m.id_medico, m.nombre, m.apellido, m.sexo, h.desc_hospital as hospital
        FROM medico m
        LEFT JOIN hospital h ON m.id_hospital = h.id_hospital
        WHERE m.id_medico = %s
        """
        df = execute_query(query, params=(dni_medico,), is_select=True)
        
        if not df.empty:
            sexo = str(df.iloc[0]['sexo']).upper()  # Convertir a mayúscula para comparar
            titulo = "Dr." if sexo == 'M' else "Dra."  # M = Dr., F = Dra.
            
            # Obtener hospital, usar "Hospital no asignado" si es NULL
            hospital = df.iloc[0]['hospital']
            if pd.isna(hospital) or hospital is None:
                hospital = "Hospital no asignado"
            
            return {
                'id_medico': int(df.iloc[0]['id_medico']),  # Convertir a int nativo de Python
                'nombre': str(df.iloc[0]['nombre']),
                'apellido': str(df.iloc[0]['apellido']),
                'sexo': sexo,
                'titulo': titulo,  # Nuevo campo con el título apropiado
                'hospital': str(hospital)  # Nuevo campo con el hospital
            }
        return None
    except Exception as e:
        st.error(f"Error buscando médico: {e}")
        return None

def obtener_siguiente_id_estudio():
    """Obtiene el siguiente ID disponible para un nuevo estudio"""
    try:
        query = "SELECT COALESCE(MAX(id_estudio), 0) + 1 as siguiente_id FROM estudio_medico"
        df = execute_query(query, is_select=True)
        
        if not df.empty:
            return int(df.iloc[0]['siguiente_id'])
        return 1
    except Exception as e:
        st.error(f"Error obteniendo siguiente ID: {e}")
        return None

def guardar_estudio(id_paciente, id_medico, desc_estudio, fecha_estudio, resultado, archivo_url=None):
    """Guarda el estudio médico en la base de datos"""
    try:
        # Obtener el siguiente ID
        siguiente_id = obtener_siguiente_id_estudio()
        if siguiente_id is None:
            return False
        
        # NUEVO: Incluir archivo_url en el insert
        query = """
        INSERT INTO estudio_medico (id_estudio, id_paciente, id_medico, desc_estudio, fecha_estudio, resultado, archivo_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, params=(siguiente_id, id_paciente, id_medico, desc_estudio, fecha_estudio, resultado, archivo_url), is_select=False)
    except Exception as e:
        st.error(f"Error guardando estudio: {e}")
        return False

# Inicializar states
if 'step' not in st.session_state:
    st.session_state.step = 'form'
if 'paciente_data' not in st.session_state:
    st.session_state.paciente_data = None
if 'medico_data' not in st.session_state:
    st.session_state.medico_data = None
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

# Header principal
st.markdown("""
<div class="main-header">
    <div class="main-title">InfoMed</div>
    <div class="subtitle">Cargar Estudios Médicos</div>
    <div style="margin-top: 1rem; color: white; font-size: 1rem; opacity: 0.9;">
        Donde tu salud está solamente a un click de distancia 😉
    </div>
</div>
""", unsafe_allow_html=True)

# NUEVO: Función para limpiar el nombre del archivo
def limpiar_nombre_archivo(nombre):
    # Quitar tildes y caracteres especiales
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
    # Reemplazar espacios por guion bajo
    nombre = nombre.replace(' ', '_')
    # Eliminar cualquier caracter que no sea letra, número, guion bajo, punto o guion
    nombre = re.sub(r'[^A-Za-z0-9._-]', '', nombre)
    return nombre

# --- NUEVO: Crear paciente placeholder ---
def crear_paciente_placeholder(dni_paciente):
    """Crea un paciente con solo el DNI, el resto de los campos con valores dummy válidos para cumplir constraints."""
    try:
        email_placeholder = f"placeholder_{dni_paciente}@placeholder.com"
        query = """
        INSERT INTO paciente (id_paciente, apellido, nombre, fecha_de_nacimiento, sexo, provincia, ciudad, calle, altura, obra_social, email, contraseña)
        VALUES (%s, '', '', '1900-01-01', 'O', 'Sin datos', 'Sin datos', 'Sin datos', '0', 'Sin datos', %s, 'placeholder')
        """
        return execute_query(query, params=(dni_paciente, email_placeholder), is_select=False)
    except Exception as e:
        st.error(f"Error creando paciente placeholder: {e}")
        return False

if st.session_state.step == 'form':
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    st.markdown("### 📋 Ingresar el Estudio")
    
    # Formulario
    with st.form("form_cargar_estudio"):
        col1, col2 = st.columns(2)
        
        with col1:
            dni_paciente = st.text_input(
                "DNI del Paciente *",
                placeholder="Ingrese el DNI del paciente",
                help="Documento Nacional de Identidad del paciente (máximo 8 dígitos)",
                max_chars=8
            )
            
            fecha_estudio = st.date_input(
                "Fecha de Realización *",
                min_value=date(1970, 1, 1),
                max_value=date.today(),
                value=date.today(),
                help="Seleccione la fecha en que se realizó el estudio"
            )
        
        with col2:
            dni_medico = st.text_input(
                "DNI del Médico *",
                value=DNI_MEDICO_AUTENTICADO,
                disabled=True,
                help="Su Documento Nacional de Identidad (máximo 8 dígitos)",
                max_chars=8
            )
        
        desc_estudio = st.text_area(
            "Descripción del Estudio *",
            placeholder="Ej: Análisis de sangre completo, Radiografía de tórax, etc.",
            height=100,
            help="Descripción detallada del tipo de estudio realizado"
        )
        
        resultado = st.text_area(
            "Resultados del Estudio *",
            placeholder="Ingrese los resultados y observaciones del estudio médico",
            height=150,
            help="Resultados detallados, valores, observaciones y conclusiones"
        )
        
        # NUEVO: Campo para subir archivo
        archivo = st.file_uploader(
            "Adjuntar archivo o imagen del estudio (opcional)",
            type=["png", "jpg", "jpeg", "pdf"],
            help="Puedes adjuntar una imagen o PDF del estudio"
        )
        
        st.markdown("---")
        submitted = st.form_submit_button("🔍 Verificar y Continuar", use_container_width=True)
        crear_placeholder = st.form_submit_button("➕ Crear paciente placeholder y continuar", use_container_width=True)
        
        if submitted or crear_placeholder:
            # Validaciones
            if not all([dni_paciente, desc_estudio, resultado]):
                st.error("❌ Por favor complete todos los campos obligatorios (*)")
            elif not dni_paciente.strip().isdigit():
                st.error("❌ El DNI del paciente debe contener solo números")
            elif len(dni_paciente.strip()) < 7 or len(dni_paciente.strip()) > 8:
                st.error("❌ El DNI del paciente debe tener 7 u 8 dígitos")
            else:
                with st.spinner("🔍 Verificando datos..."):
                    paciente = buscar_paciente_por_dni(dni_paciente.strip())
                    if not paciente:
                        if crear_placeholder:
                            creado = crear_paciente_placeholder(dni_paciente.strip())
                            if creado:
                                st.success("Paciente placeholder creado. Continúe con la carga del estudio.")
                                paciente = buscar_paciente_por_dni(dni_paciente.strip())
                                # Buscar médico (ya autenticado)
                                medico = buscar_medico_por_dni(DNI_MEDICO_AUTENTICADO)
                                if not medico:
                                    st.error(f"❌ No se encontró un médico con el DNI: {DNI_MEDICO_AUTENTICADO}")
                                    st.info("💡 Verifique que su usuario esté correctamente registrado como médico en el sistema")
                                else:
                                    # NUEVO: Subir archivo si existe
                                    archivo_url = None
                                    if archivo is not None:
                                        supabase = get_supabase_client()
                                        timestamp = int(time.time())
                                        nombre_archivo = f"{dni_paciente.strip()}_{fecha_estudio}_{timestamp}_{archivo.name}"
                                        nombre_archivo = limpiar_nombre_archivo(nombre_archivo)
                                        data = archivo.read()
                                        try:
                                            res = supabase.storage.from_(SUPABASE_BUCKET).upload(nombre_archivo, data, {"content-type": archivo.type})
                                            archivo_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(nombre_archivo)
                                        except Exception as e:
                                            st.error(f"Error subiendo el archivo a Supabase Storage: {e}")
                                            archivo_url = None
                                    st.session_state.paciente_data = paciente
                                    st.session_state.medico_data = medico
                                    st.session_state.form_data = {
                                        'dni_paciente': dni_paciente.strip(),
                                        'dni_medico': DNI_MEDICO_AUTENTICADO,
                                        'desc_estudio': desc_estudio.strip(),
                                        'fecha_estudio': fecha_estudio,
                                        'resultado': resultado.strip(),
                                        'archivo_url': archivo_url
                                    }
                                    st.session_state.step = 'confirmation'
                                    st.success("✅ Datos verificados correctamente")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error("No se pudo crear el paciente placeholder. Intente nuevamente.")
                        elif submitted:
                            st.warning(f"No se encontró un paciente con el DNI: {dni_paciente}")
                            st.info("💡 Si el paciente aún no está registrado, puede crearlo como placeholder para asociar el estudio a su DNI usando el botón de abajo.")
                    else:
                        # Buscar médico (ya autenticado)
                        medico = buscar_medico_por_dni(DNI_MEDICO_AUTENTICADO)
                        if not medico:
                            st.error(f"❌ No se encontró un médico con el DNI: {DNI_MEDICO_AUTENTICADO}")
                            st.info("💡 Verifique que su usuario esté correctamente registrado como médico en el sistema")
                        else:
                            # NUEVO: Subir archivo si existe
                            archivo_url = None
                            if archivo is not None:
                                supabase = get_supabase_client()
                                timestamp = int(time.time())
                                nombre_archivo = f"{dni_paciente.strip()}_{fecha_estudio}_{timestamp}_{archivo.name}"
                                nombre_archivo = limpiar_nombre_archivo(nombre_archivo)
                                data = archivo.read()
                                try:
                                    res = supabase.storage.from_(SUPABASE_BUCKET).upload(nombre_archivo, data, {"content-type": archivo.type})
                                    archivo_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(nombre_archivo)
                                except Exception as e:
                                    st.error(f"Error subiendo el archivo a Supabase Storage: {e}")
                                    archivo_url = None
                            st.session_state.paciente_data = paciente
                            st.session_state.medico_data = medico
                            st.session_state.form_data = {
                                'dni_paciente': dni_paciente.strip(),
                                'dni_medico': DNI_MEDICO_AUTENTICADO,
                                'desc_estudio': desc_estudio.strip(),
                                'fecha_estudio': fecha_estudio,
                                'resultado': resultado.strip(),
                                'archivo_url': archivo_url
                            }
                            st.session_state.step = 'confirmation'
                            st.success("✅ Datos verificados correctamente")
                            time.sleep(1)
                            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 'dni_correction':
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    st.markdown("### 📝 Corrección de DNI")
    
    st.markdown("""
    <div class="dni-correction-form">
        <h4>🔄 Corrija los DNI según sea necesario</h4>
        <p>Los demás datos del estudio se mantendrán igual.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_corregir_dni"):
        col1, col2 = st.columns(2)
        
        with col1:
            dni_paciente = st.text_input(
                "DNI del Paciente *",
                value=st.session_state.form_data.get('dni_paciente', ''),
                placeholder="Ingrese el DNI del paciente",
                help="Documento Nacional de Identidad del paciente (máximo 8 dígitos)",
                max_chars=8
            )
        
        with col2:
            dni_medico = st.text_input(
                "DNI del Médico *",
                value=DNI_MEDICO_AUTENTICADO,
                disabled=True,
                help="Su Documento Nacional de Identidad (máximo 8 dígitos)",
                max_chars=8
            )
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state.step = 'confirmation'
                st.rerun()
        
        with col2:
            submitted = st.form_submit_button("🔍 Verificar DNI", use_container_width=True)
        
        if submitted:
            # Validaciones
            if not dni_paciente:
                st.error("❌ Por favor complete el campo de DNI del paciente")
            elif not dni_paciente.strip().isdigit():
                st.error("❌ El DNI del paciente debe contener solo números")
            elif len(dni_paciente.strip()) < 7 or len(dni_paciente.strip()) > 8:
                st.error("❌ El DNI del paciente debe tener 7 u 8 dígitos")
            else:
                with st.spinner("🔍 Verificando datos..."):
                    # Buscar paciente
                    paciente = buscar_paciente_por_dni(dni_paciente.strip())
                    if not paciente:
                        st.error(f"❌ No se encontró un paciente con el DNI: {dni_paciente}")
                        st.info("💡 Verifique que el DNI sea correcto y que el paciente esté registrado en el sistema")
                    else:
                        # Buscar médico (ya autenticado)
                        medico = buscar_medico_por_dni(DNI_MEDICO_AUTENTICADO)
                        if not medico:
                            st.error(f"❌ No se encontró un médico con el DNI: {DNI_MEDICO_AUTENTICADO}")
                            st.info("💡 Verifique que su usuario esté correctamente registrado como médico en el sistema")
                        else:
                            # Actualizar datos y volver a confirmación
                            st.session_state.paciente_data = paciente
                            st.session_state.medico_data = medico
                            st.session_state.form_data['dni_paciente'] = dni_paciente.strip()
                            st.session_state.form_data['dni_medico'] = DNI_MEDICO_AUTENTICADO
                            st.session_state.step = 'confirmation'
                            st.success("✅ DNI corregido correctamente")
                            time.sleep(1)
                            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 'confirmation':
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    st.markdown("### ✅ ¡Un último paso!")
    
    st.markdown("""
    <div class="confirmation-box">
        <h4>¿Puede confirmar si este es el DNI del paciente para el que desea cargar este estudio?</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar información del paciente
    st.markdown(f"""
    <div class="patient-info">
        <h3>👤 {st.session_state.paciente_data['nombre']} {st.session_state.paciente_data['apellido']}</h3>
        <p><strong>DNI:</strong> {st.session_state.form_data['dni_paciente']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar resumen del estudio completo
    st.markdown("### 📄 Resumen del Estudio")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Fecha:** {st.session_state.form_data['fecha_estudio']}")
        # MODIFICADO: Usar el título apropiado (Dr./Dra.) según el sexo
        st.info(f"**Médico:** {st.session_state.medico_data['titulo']} {st.session_state.medico_data['nombre']} {st.session_state.medico_data['apellido']}")
    
    with col2:
        st.info(f"**Descripción:** {st.session_state.form_data['desc_estudio']}")
        st.info(f"**Resultados:** {st.session_state.form_data['resultado']}")
    
    # Botones de confirmación
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.step = 'form'
            st.session_state.paciente_data = None
            st.session_state.medico_data = None
            st.session_state.form_data = {}
            st.rerun()
    
    with col2:
        if st.button("📝 Corregir DNI", use_container_width=True):
            st.session_state.step = 'dni_correction'
            st.rerun()
    
    with col3:
        if st.button("✅ Confirmar y Guardar", use_container_width=True):
            with st.spinner("💾 Guardando estudio..."):
                # Guardar estudio
                if guardar_estudio(
                    st.session_state.paciente_data['id_paciente'],
                    st.session_state.medico_data['id_medico'],
                    st.session_state.form_data['desc_estudio'],
                    st.session_state.form_data['fecha_estudio'],
                    st.session_state.form_data['resultado'],
                    archivo_url=st.session_state.form_data.get('archivo_url')
                ):
                    st.session_state.step = 'success'
                    st.success("✅ Guardando...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Error al guardar el estudio. Por favor intente nuevamente.")
                    st.info("💡 Verifique su conexión a internet y que todos los datos sean válidos")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 'success':
    st.markdown("""
    <div class="success-message">
        <h2>🎉 ¡Estudio cargado con éxito!</h2>
        <p>El estudio médico ha sido registrado correctamente en el sistema.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar resumen final
    st.markdown("### 📋 Resumen del Estudio Cargado")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"**Paciente:** {st.session_state.paciente_data['nombre']} {st.session_state.paciente_data['apellido']}")
        st.success(f"**Fecha:** {st.session_state.form_data['fecha_estudio']}")
        st.success(f"**Hospital:** {st.session_state.medico_data['hospital']}")
    
    with col2:
        # MODIFICADO: Usar el título apropiado (Dr./Dra.) según el sexo
        st.success(f"**Médico:** {st.session_state.medico_data['titulo']} {st.session_state.medico_data['nombre']} {st.session_state.medico_data['apellido']}")
        st.success(f"**Estudio:** {st.session_state.form_data['desc_estudio']}")
        st.success(f"**Resultado:** {st.session_state.form_data['resultado']}")
    
    if st.button("🔄 Cargar Otro Estudio", use_container_width=True):
        st.session_state.step = 'form'
        st.session_state.paciente_data = None
        st.session_state.medico_data = None
        st.session_state.form_data = {}
        st.rerun()

# Botón para volver al perfil
if st.button("🔙 Volver al perfil"):
    st.switch_page("Inicio.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>InfoMed - Sistema de Gestión Médica</p>
    <p>Desarrollado para facilitar la atención médica 🏥</p>
</div>
""", unsafe_allow_html=True)