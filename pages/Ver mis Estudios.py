import streamlit as st
import sys
import os
# Agregar el directorio padre al path para importar funciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funciones de autenticación desde Inicio.py
from Inicio import solo_paciente_autenticado, verificar_autenticacion, get_db_connection

# Control de acceso: solo pacientes autenticados
solo_paciente_autenticado()

import pandas as pd
from datetime import datetime

def execute_query_simple(query, params=None):
    """
    Ejecuta una consulta SQL usando get_db_connection
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=colnames)
        
        cursor.close()
        conn.close()
        return df
        
    except Exception as e:
        st.error(f"Error ejecutando consulta: {e}")
        if conn:
            conn.close()
        return pd.DataFrame()

def obtener_estudios_paciente(id_paciente):
    """
    Obtiene todos los estudios de un paciente específico con información completa
    """
    query = """
    SELECT 
        e.id_estudio,
        e.desc_estudio,
        e.fecha_estudio,
        e.resultado,
        m.nombre || ' ' || m.apellido as nombre_medico,
        h.desc_hospital as hospital,
        p.nombre || ' ' || p.apellido as nombre_paciente
    FROM estudio_medico e
    JOIN medico m ON e.id_medico = m.id_medico
    JOIN hospital h ON m.id_hospital = h.id_hospital
    JOIN paciente p ON e.id_paciente = p.id_paciente
    WHERE e.id_paciente = %s
    ORDER BY e.fecha_estudio DESC
    """
    
    return execute_query_simple(query, params=(id_paciente,))

def obtener_medicos_paciente(id_paciente):
    """
    Obtiene la lista de médicos que han atendido al paciente para filtros
    """
    query = """
    SELECT DISTINCT 
        m.id_medico,
        m.nombre || ' ' || m.apellido as nombre_medico
    FROM estudio_medico e
    JOIN medico m ON e.id_medico = m.id_medico
    WHERE e.id_paciente = %s
    ORDER BY nombre_medico
    """
    return execute_query_simple(query, params=(id_paciente,))

def obtener_fechas_estudios_paciente(id_paciente):
    """
    Obtiene las fechas únicas de estudios del paciente para filtros
    """
    query = """
    SELECT DISTINCT fecha_estudio
    FROM estudio_medico
    WHERE id_paciente = %s
    ORDER BY fecha_estudio DESC
    """
    return execute_query_simple(query, params=(id_paciente,))

def verificar_paciente_por_dni(dni):
    """
    Verifica si existe un paciente con el DNI dado y retorna su información
    """
    query = """
    SELECT id_paciente, nombre, apellido, dni
    FROM paciente 
    WHERE dni = %s
    """
    return execute_query_simple(query, params=(dni,))

def obtener_paciente_por_id(id_paciente):
    """
    Obtiene la información completa de un paciente por su ID
    """
    query = """
    SELECT id_paciente, nombre, apellido, dni, fecha_nacimiento, sexo, direccion, codigo_postal, obra_social
    FROM paciente 
    WHERE id_paciente = %s
    """
    return execute_query_simple(query, params=(id_paciente,))

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Ver mis Estudios",
        page_icon="📋",
        layout="wide"
    )
    
    # Verificar autenticación usando el nuevo sistema
    if not verificar_autenticacion():
        st.error("🔐 Debes iniciar sesión para acceder a esta página")
        st.info("Por favor, regresa a la página principal e inicia sesión.")
        if st.button("🏠 Ir a la página principal"):
            st.switch_page("Inicio.py")
        st.stop()
    
    # Verificar que el usuario es un paciente
    if st.session_state.get("tipo_usuario") != "paciente":
        st.error("❌ Solo los pacientes pueden acceder a esta página.")
        if st.button("🔙 Volver al perfil"):
            st.switch_page("Inicio.py")
        st.stop()
    
    # Obtener información del paciente desde el session state
    usuario = st.session_state.usuario_autenticado
    
    # Obtener el ID del paciente correctamente
    id_paciente = usuario.get('id_paciente') or usuario.get('dni') or usuario.get('id')
    nombre_paciente = f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}"
    dni_paciente = usuario.get('dni') or usuario.get('id_paciente')
    
    # CSS personalizado
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #1f77b4;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 2rem;
            padding: 1rem;
            background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
            border-radius: 10px;
            border: 2px solid #1f77b4;
        }
        
        .study-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .study-card:hover {
            border-color: #1f77b4;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .study-title {
            color: #1f77b4;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .study-date {
            color: #666;
            font-style: italic;
        }
        
        .study-description {
            margin-top: 0.5rem;
            color: #333;
        }
        
        .no-studies {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    

    # --- Main Application ---
    st.markdown(
        """
        <h1 style='text-align: center; color: #000000; font-size: 45px; font-weight: bold;'>
            📋 Mis Estudios Médicos
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div style="text-align: center; background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: #2c3e50; margin: 0;">👤 {nombre_paciente}</h3>
        <p style="color: #7f8c8d; margin: 5px 0;">DNI: {dni_paciente}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener estudios del paciente con manejo de errores
    try:
        estudios_df = obtener_estudios_paciente(id_paciente)
        
        if estudios_df.empty:
            st.markdown("""
            <div class="no-studies">
                <h3>📋 No tienes estudios registrados</h3>
                <p>Aún no se han cargado estudios médicos en tu historial.</p>
            </div>
            """, unsafe_allow_html=True)
            return
            
    except Exception as e:
        st.error(f"❌ Error al obtener los estudios: {str(e)}")
        st.info("💡 Verifique la conexión a la base de datos")
        return
    
    # Sección de filtros
    with st.expander("🔍 Filtros de búsqueda", expanded=False ):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por médico
            try:
                medicos_df = obtener_medicos_paciente(id_paciente)
                if not medicos_df.empty:
                    medicos_options = ["Todos los médicos"] + medicos_df['nombre_medico'].tolist()
                else:
                    medicos_options = ["Todos los médicos"]
                medico_seleccionado = st.selectbox("Filtrar por médico:", medicos_options)
            except Exception as e:
                st.warning(f"Error al cargar médicos: {str(e)}")
                medico_seleccionado = "Todos los médicos"
        
        with col2:
            # Filtro por fecha
            try:
                fechas_df = obtener_fechas_estudios_paciente(id_paciente)
                if not fechas_df.empty:
                    fechas_options = ["Todas las fechas"] + [str(fecha) for fecha in fechas_df['fecha_estudio'].tolist()]
                else:
                    fechas_options = ["Todas las fechas"]
                fecha_seleccionada = st.selectbox("Filtrar por fecha:", fechas_options)
            except Exception as e:
                st.warning(f"Error al cargar fechas: {str(e)}")
                fecha_seleccionada = "Todas las fechas"
        
        with col3:
            # Filtro por palabra clave en descripción
            buscar_texto = st.text_input("Buscar en descripción:", placeholder="Ej: radiografía, análisis...")
    
    # Aplicar filtros
    estudios_filtrados = estudios_df.copy()
    
    if medico_seleccionado != "Todos los médicos":
        estudios_filtrados = estudios_filtrados[estudios_filtrados['nombre_medico'] == medico_seleccionado]
    
    if fecha_seleccionada != "Todas las fechas":
        estudios_filtrados = estudios_filtrados[estudios_filtrados['fecha_estudio'].astype(str) == fecha_seleccionada]
    
    if buscar_texto:
        estudios_filtrados = estudios_filtrados[
            estudios_filtrados['desc_estudio'].str.contains(buscar_texto, case=False, na=False)
        ]
    
    # Mostrar contador de estudios
    total_estudios = len(estudios_filtrados)
    if total_estudios > 0:
        st.info(f"📊 Mostrando {total_estudios} estudio(s) encontrado(s)")
    else:
        st.warning("No se encontraron estudios con los filtros aplicados")
        return
    
    # Mostrar estudios como tarjetas usando Streamlit nativo
    for index, estudio in estudios_filtrados.iterrows():
        # Formatear fecha
        fecha_formatted = estudio['fecha_estudio'].strftime("%d/%m/%Y") if pd.notna(estudio['fecha_estudio']) else "Fecha no disponible"
        
        # Crear expander para cada estudio (actúa como frame)
        with st.expander(f"📋 {estudio['desc_estudio']} - 📅 {fecha_formatted}", expanded=True):
            # Información del paciente
            st.info(f"👤 **Paciente:** {estudio['nombre_paciente']}")
            
            # Información del médico y hospital
            st.success(f"👨‍⚕️ **Médico:** {estudio['nombre_medico']} | 🏥 **Hospital:** {estudio['hospital']}")
            
            # Resultados
            if pd.notna(estudio['resultado']) and estudio['resultado']:
                st.markdown("**📋 Resultados:**")
                st.markdown(f"*{estudio['resultado']}*")
            else:
                st.warning("📋 **Resultados:** No disponibles")
    
    # Estadísticas adicionales
    if total_estudios > 1:
        with st.expander("📈 Estadísticas de mis estudios"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de estudios", total_estudios)
            
            with col2:
                medicos_unicos = estudios_filtrados['nombre_medico'].nunique()
                st.metric("Médicos diferentes", medicos_unicos)
            
            with col3:
                hospitales_unicos = estudios_filtrados['hospital'].nunique()
                st.metric("Hospitales visitados", hospitales_unicos)
            
            # Mostrar estudios por mes (si hay datos suficientes)
            if total_estudios > 3:
                st.subheader("📅 Estudios por mes")
                estudios_por_mes = estudios_filtrados.copy()
                estudios_por_mes['mes_año'] = estudios_por_mes['fecha_estudio'].dt.strftime('%Y-%m')
                estudios_por_mes_count = estudios_por_mes.groupby('mes_año').size().reset_index(name='cantidad')
                st.bar_chart(estudios_por_mes_count.set_index('mes_año')['cantidad'])
    
    # Botón para exportar (opcional)
    if st.button("📥 Descargar mis estudios"):
        csv = estudios_filtrados.to_csv(index=False)
        st.download_button(
            label="Descargar como CSV",
            data=csv,
            file_name=f"mis_estudios_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    if st.button("🔙 Volver al perfil"):
        st.switch_page("Inicio.py")

if __name__ == "__main__":
    main()