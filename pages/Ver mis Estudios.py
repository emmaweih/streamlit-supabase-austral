import streamlit as st
import sys
import os

# Agregar el directorio padre al path para importar funciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funciones de autenticación desde Inicio.py
from Inicio import verificar_autenticacion, verificar_permiso_pagina

# Configuración de la página
st.set_page_config(
    page_title="Ver mis Estudios",
    page_icon="📋",
    layout="wide"
)

# Verificar autenticación y permisos
if not verificar_autenticacion():
    st.error("🔐 Debes iniciar sesión para acceder a esta página")
    st.info("Por favor, regresa a la página principal e inicia sesión.")
    if st.button("🏠 Ir a la página principal"):
        st.switch_page("Inicio.py")
    st.stop()

# Verificar permisos específicos para esta página
permiso = verificar_permiso_pagina("Ver mis Estudios")
if not permiso['permitido']:
    st.error(f"❌ {permiso['mensaje']}")
    st.info("Esta página solo está disponible para pacientes.")
    if st.button("🔙 Volver al perfil"):
        st.switch_page("Inicio.py")
    st.stop()

# Contenido de la página
st.title("📋 Ver mis Estudios")
st.markdown("---")

# Información del usuario
usuario = st.session_state.usuario_autenticado
st.info(f"👤 Paciente: {usuario['nombre']} {usuario['apellido']}")

# Filtros de búsqueda
st.subheader("🔍 Filtros de Búsqueda")
col1, col2, col3 = st.columns(3)

with col1:
    fecha_desde = st.date_input("📅 Desde:")
    fecha_hasta = st.date_input("📅 Hasta:")

with col2:
    tipo_estudio = st.selectbox("🧪 Tipo de Estudio:", 
                               ["Todos", "Análisis de Sangre", "Radiografía", "Ecografía", "Tomografía", "Resonancia"])

with col3:
    medico = st.text_input("👨‍⚕️ Médico:")
    hospital = st.text_input("🏥 Hospital:")

# Botón de búsqueda
if st.button("🔍 Buscar Estudios", use_container_width=True):
    st.info("🔧 Función de búsqueda en desarrollo...")

st.markdown("---")

# Lista de estudios (placeholder)
st.subheader("📊 Mis Estudios Médicos")

# Estudios de ejemplo
estudios_ejemplo = [
    {
        "fecha": "2024-01-15",
        "tipo": "Análisis de Sangre",
        "medico": "Dr. García",
        "hospital": "Hospital Austral",
        "estado": "Completado",
        "resultado": "Normal"
    },
    {
        "fecha": "2024-01-10",
        "tipo": "Radiografía de Tórax",
        "medico": "Dr. López",
        "hospital": "Hospital Austral",
        "estado": "Completado",
        "resultado": "Normal"
    },
    {
        "fecha": "2024-01-05",
        "tipo": "Ecografía Abdominal",
        "medico": "Dr. Martínez",
        "hospital": "Hospital Austral",
        "estado": "Pendiente",
        "resultado": "En proceso"
    }
]

# Mostrar estudios
for i, estudio in enumerate(estudios_ejemplo):
    with st.expander(f"📋 {estudio['tipo']} - {estudio['fecha']}", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Fecha:** {estudio['fecha']}")
            st.write(f"**Tipo:** {estudio['tipo']}")
            st.write(f"**Médico:** {estudio['medico']}")
        
        with col2:
            st.write(f"**Hospital:** {estudio['hospital']}")
            st.write(f"**Estado:** {estudio['estado']}")
            st.write(f"**Resultado:** {estudio['resultado']}")
        
        # Botones de acción
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("📄 Ver Detalles", key=f"detalles_{i}"):
                st.info("🔧 Función de detalles en desarrollo...")
        
        with col_btn2:
            if st.button("📥 Descargar", key=f"descargar_{i}"):
                st.info("🔧 Función de descarga en desarrollo...")
        
        with col_btn3:
            if st.button("📧 Compartir", key=f"compartir_{i}"):
                st.info("🔧 Función de compartir en desarrollo...")

st.markdown("---")

# Estadísticas
st.subheader("📈 Estadísticas")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Estudios", "15")
with col2:
    st.metric("Completados", "12")
with col3:
    st.metric("Pendientes", "3")
with col4:
    st.metric("Este Mes", "5")

# Botón para volver
if st.button("🔙 Volver al Perfil"):
    st.switch_page("Inicio.py")
