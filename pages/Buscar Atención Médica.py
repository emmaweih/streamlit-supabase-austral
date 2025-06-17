import streamlit as st
import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import execute_query


# --- Page Configuration ---
st.set_page_config(
    page_title="InfoMed - Buscar Atención Médica",
    page_icon="🔍",
    layout="wide"
)
def buscar_por_especialidad():
    """
    Función para buscar atención médica por especialidad
    Esta función debe estar en tu archivo de funciones (f.py o similar)
    """
    
    # Estilos CSS específicos para esta sección
    st.markdown("""
    <style>
    /* Estilos para la búsqueda por especialidad */
    .especialidad-header {
        text-align: center;
        background: linear-gradient(135deg, #4A90E2 0%, #7BB3F0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .especialidad-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .especialidad-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Tarjetas de hospital mejoradas */
    .hospital-card-especialidad {
        background: white;
        border: 2px solid #E3F2FD;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .hospital-card-especialidad:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.2);
        border-color: #4A90E2;
    }
    
    .hospital-name-especialidad {
        color: #1565C0;
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
    }
    
    .hospital-info-especialidad {
        color: #424242;
        font-size: 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
    }
    
    .hospital-icon-especialidad {
        margin-right: 0.8rem;
        color: #4A90E2;
        font-size: 1.1rem;
    }
    
    /* Selectbox personalizado */
    .stSelectbox > div > div {
        border: 2px solid #E3F2FD;
        border-radius: 8px;
        font-size: 1rem;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #4A90E2;
        box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
    }
    
    /* Mensaje de no resultados */
    .no-results-especialidad {
        text-align: center;
        padding: 2rem;
        background: #F8F9FA;
        border-radius: 12px;
        color: #666;
        font-size: 1.1rem;
        border: 2px dashed #DDD;
    }
    
    /* Contador de resultados */
    .results-counter {
        background: linear-gradient(135deg, #E8F5E8 0%, #F0F8FF 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        border-left: 4px solid #4A90E2;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header de la sección
    st.markdown("""
    <div class="especialidad-header">
        <div class="especialidad-title">🏥 Buscar por Especialidad</div>
        <div class="especialidad-subtitle">Selecciona la especialidad médica que necesitas</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Funciones auxiliares
    def obtener_especialidades():
        """Obtiene todas las especialidades de la base de datos"""
        query = """
        SELECT id_especialidad, desc_especialidad 
        FROM especialidades 
        ORDER BY desc_especialidad
        """
        try:
            return execute_query(query)
        except Exception as e:
            st.error(f"Error al obtener especialidades: {str(e)}")
            return pd.DataFrame()
    
    def obtener_hospitales_por_especialidad(id_especialidad):
        """Obtiene todos los hospitales que ofrecen una especialidad específica"""
        query = """
        SELECT DISTINCT h.desc_hospital, h.direccion, h.telefono
        FROM hospital h
        INNER JOIN hospital_especialidades he ON h.id_hospital = he.id_hospital
        WHERE he.id_especialidad = %s
        ORDER BY h.desc_hospital
        """
        try:
            return execute_query(query, (id_especialidad,))
        except Exception as e:
            st.error(f"Error al obtener hospitales: {str(e)}")
            return pd.DataFrame()
    
    def mostrar_hospital_card(hospital_row):
        """Muestra una tarjeta individual de hospital"""
        # Convertir fila de DataFrame a diccionario si es necesario
        if hasattr(hospital_row, 'to_dict'):
            hospital = hospital_row.to_dict()
        else:
            hospital = hospital_row
        
        # Manejar valores None o NaN
        direccion = hospital.get('direccion', 'No disponible')
        if pd.isna(direccion):
            direccion = 'No disponible'
            
        telefono = hospital.get('telefono', 'No disponible')
        if pd.isna(telefono):
            telefono = 'No disponible'
        
        st.markdown(f"""
        <div class="hospital-card-especialidad">
            <div class="hospital-name-especialidad">
                <span class="hospital-icon-especialidad">🏥</span>
                {hospital['desc_hospital']}
            </div>
            <div class="hospital-info-especialidad">
                <span class="hospital-icon-especialidad">📍</span>
                <strong>Dirección:</strong> &nbsp; {direccion}
            </div>
            <div class="hospital-info-especialidad">
                <span class="hospital-icon-especialidad">📞</span>
                <strong>Teléfono:</strong> &nbsp; {telefono}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Obtener especialidades
    with st.spinner("🔄 Cargando especialidades..."):
        especialidades = obtener_especialidades()
    
    # Verificar si hay especialidades
    if especialidades is None or especialidades.empty:
        st.error("❌ No se pudieron cargar las especialidades. Verifique la conexión a la base de datos.")
        return
    
    # Crear selectbox con las especialidades
    st.markdown("### 🔍 Seleccione una Especialidad")
    
    # Crear opciones para el selectbox
    opciones_especialidades = ["-- Seleccione una especialidad --"] + especialidades['desc_especialidad'].tolist()
    
    especialidad_seleccionada = st.selectbox(
        "Especialidad médica:",
        opciones_especialidades,
        key="especialidad_select",
        help="Seleccione la especialidad médica que está buscando"
    )
    
    # Si se seleccionó una especialidad válida
    if especialidad_seleccionada and especialidad_seleccionada != "-- Seleccione una especialidad --":
        
        # Encontrar el ID de la especialidad seleccionada
        id_especialidad = None
        for idx, row in especialidades.iterrows():
            if row['desc_especialidad'] == especialidad_seleccionada:
                id_especialidad = row['id_especialidad']
                break
        
        if id_especialidad:
            # Buscar hospitales
            with st.spinner(f"🔍 Buscando hospitales para **{especialidad_seleccionada}**..."):
                hospitales = obtener_hospitales_por_especialidad(id_especialidad)
            
            # Espacio
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Mostrar resultados
            if hospitales is not None and not hospitales.empty:
                
                # Contador de resultados
                st.markdown(f"""
                <div class="results-counter">
                    <h4 style="margin: 0; color: #2E7D32;">
                        ✅ Se encontraron <strong>{len(hospitales)} hospitales</strong> 
                        que ofrecen <strong>{especialidad_seleccionada}</strong>
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 🏥 Resultados de la búsqueda")
                
                # Mostrar cada hospital como una tarjeta
                for idx, hospital in hospitales.iterrows():
                    mostrar_hospital_card(hospital)
                
                # Información adicional
                st.markdown("---")
                st.markdown("""
                <div style='text-align: center; color: #666; padding: 1rem;'>
                    <p>💡 <strong>Consejo:</strong> Te recomendamos llamar antes de concurrir para confirmar horarios y disponibilidad.</p>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                # No se encontraron resultados
                st.markdown(f"""
                <div class="no-results-especialidad">
                    <h3 style="color: #FF6B6B; margin-bottom: 1rem;">😔 No se encontraron hospitales</h3>
                    <p style="font-size: 1.1rem; margin-bottom: 1rem;">
                        No hay hospitales disponibles para la especialidad 
                        <strong>{especialidad_seleccionada}</strong>
                    </p>
                    <p style="color: #888;">
                        • Intenta seleccionar otra especialidad<br>
                        • Verifica que la especialidad esté disponible en tu zona<br>
                        • Contacta al administrador si el problema persiste
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.error("❌ No se pudo obtener el ID de la especialidad seleccionada.")
    
    else:
        # Mostrar mensaje de ayuda cuando no hay selección
        st.info("👆 Selecciona una especialidad médica del menú desplegable para ver los hospitales disponibles.")

def buscar_por_sintomas(sintoma_a, sintoma_b):
    """
    Busca especialidades y hospitales basados en dos síntomas dados.
    
    Args:
        sintoma_a (str): Descripción del primer síntoma
        sintoma_b (str): Descripción del segundo síntoma
    
    Returns:
        list: Lista de diccionarios con especialidad, hospital, dirección y teléfono
    """
    
    query = """
    SELECT DISTINCT 
        e.desc_especialidad as especialidad,
        h.desc_hospital as hospital,
        h.direccion,
        h.telefono
    FROM patologia p
    INNER JOIN sintoma s1 ON (p.id_sintoma_1 = s1.id_sintoma OR p.id_sintoma_2 = s1.id_sintoma)
    INNER JOIN sintoma s2 ON (p.id_sintoma_1 = s2.id_sintoma OR p.id_sintoma_2 = s2.id_sintoma)
    INNER JOIN patologia_especialidades pe ON p.id_patologia = pe.id_patologia
    INNER JOIN especialidades e ON pe.id_especialidad = e.id_especialidad
    INNER JOIN patologia_hospital ph ON p.id_patologia = ph.id_patologia
    INNER JOIN hospital h ON ph.id_hospital = h.id_hospital
    WHERE s1.desc_sintoma = %s 
      AND s2.desc_sintoma = %s
      AND s1.id_sintoma != s2.id_sintoma
    ORDER BY e.desc_especialidad, h.desc_hospital;
    """
    
    try:
        # Ejecutar la consulta usando tu función execute_query
        df_results = execute_query(query, params=(sintoma_a, sintoma_b))
        
        # Convertir el DataFrame a lista de diccionarios
        if not df_results.empty:
            results = df_results.to_dict('records')
            return results
        else:
            return []
            
    except Exception as e:
        print(f"Error en buscar_por_sintomas: {e}")
        return []


# Función auxiliar para obtener todos los síntomas disponibles (útil para poblar los selectbox)
def obtener_sintomas():
    """
    Obtiene todos los síntomas disponibles en la base de datos.
    
    Returns:
        list: Lista de descripciones de síntomas
    """
    query = "SELECT desc_sintoma FROM sintoma ORDER BY desc_sintoma;"
    
    try:
        df_sintomas = execute_query(query)
        if not df_sintomas.empty:
            return df_sintomas['desc_sintoma'].tolist()
        else:
            return []
    except Exception as e:
        print(f"Error al obtener síntomas: {e}")
        return []


def buscar_por_sintomas():
    """
    Función principal para la búsqueda por síntomas - integrada con tu estilo
    """
    
    # Estilos CSS específicos para síntomas (similar a tu función de especialidades)
    st.markdown("""
    <style>
    .sintomas-header {
        text-align: center;
        background: linear-gradient(135deg, #E91E63 0%, #F48FB1 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .sintomas-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .sintomas-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .hospital-card-sintomas {
        background: white;
        border: 2px solid #FCE4EC;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .hospital-card-sintomas:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(233, 30, 99, 0.2);
        border-color: #E91E63;
    }
    
    .specialty-tag {
        background: linear-gradient(135deg, #E91E63 0%, #F48FB1 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 0.5rem;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header de la sección
    st.markdown("""
    <div class="sintomas-header">
        <div class="sintomas-title">🩺 Buscar por Síntomas</div>
        <div class="sintomas-subtitle">Selecciona dos síntomas y te ayudamos a encontrar la especialidad</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Funciones auxiliares locales
    def obtener_sintomas_local():
        """Obtiene todos los síntomas disponibles en la base de datos"""
        query = "SELECT desc_sintoma FROM sintoma ORDER BY desc_sintoma;"
        try:
            df_sintomas = execute_query(query)
            if not df_sintomas.empty:
                return df_sintomas['desc_sintoma'].tolist()
            else:
                return []
        except Exception as e:
            st.error(f"Error al obtener síntomas: {str(e)}")
            return []

    def buscar_por_sintomas_local(sintoma_a, sintoma_b):
        """Busca especialidades y hospitales basados en dos síntomas dados"""
        query = """
        SELECT DISTINCT 
            e.desc_especialidad as especialidad,
            h.desc_hospital as hospital,
            h.direccion,
            h.telefono
        FROM patologia p
        INNER JOIN sintoma s1 ON (p.id_sintoma_1 = s1.id_sintoma OR p.id_sintoma_2 = s1.id_sintoma)
        INNER JOIN sintoma s2 ON (p.id_sintoma_1 = s2.id_sintoma OR p.id_sintoma_2 = s2.id_sintoma)
        INNER JOIN patologia_especialidades pe ON p.id_patologia = pe.id_patologia
        INNER JOIN especialidades e ON pe.id_especialidad = e.id_especialidad
        INNER JOIN patologia_hospital ph ON p.id_patologia = ph.id_patologia
        INNER JOIN hospital h ON ph.id_hospital = h.id_hospital
        WHERE s1.desc_sintoma = %s 
          AND s2.desc_sintoma = %s
          AND s1.id_sintoma != s2.id_sintoma
        ORDER BY e.desc_especialidad, h.desc_hospital;
        """
        
        try:
            df_results = execute_query(query, params=(sintoma_a, sintoma_b))
            if not df_results.empty:
                return df_results.to_dict('records')
            else:
                return []
        except Exception as e:
            st.error(f"Error en la búsqueda: {str(e)}")
            return []

    def mostrar_resultado_sintomas(resultado):
        """Muestra una tarjeta de resultado con especialidad y hospital"""
        direccion = resultado.get('direccion', 'No disponible')
        if pd.isna(direccion):
            direccion = 'No disponible'
            
        telefono = resultado.get('telefono', 'No disponible')
        if pd.isna(telefono):
            telefono = 'No disponible'
        
        st.markdown(f"""
        <div class="hospital-card-sintomas">
            <div style="margin-bottom: 1rem;">
                <span class="specialty-tag">{resultado['especialidad']}</span>
            </div>
            <div class="hospital-name-especialidad">
                <span class="hospital-icon-especialidad">🏥</span>
                {resultado['hospital']}
            </div>
            <div class="hospital-info-especialidad">
                <span class="hospital-icon-especialidad">📍</span>
                <strong>Dirección:</strong> &nbsp; {direccion}
            </div>
            <div class="hospital-info-especialidad">
                <span class="hospital-icon-especialidad">📞</span>
                <strong>Teléfono:</strong> &nbsp; {telefono}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Obtener síntomas
    with st.spinner("🔄 Cargando síntomas..."):
        sintomas_disponibles = obtener_sintomas_local()
    
    if not sintomas_disponibles:
        st.error("❌ No se pudieron cargar los síntomas. Verifique la conexión a la base de datos.")
        return
    
    # Crear selectboxes
    st.markdown("### 🔍 Seleccione dos síntomas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        opciones_sintoma_a = ["-- Seleccione el primer síntoma --"] + sintomas_disponibles
        sintoma_a = st.selectbox(
            "Síntoma A:",
            opciones_sintoma_a,
            key="sintoma_a_select",
            help="Seleccione el primer síntoma"
        )
    
    with col2:
        # Filtrar síntomas para evitar seleccionar el mismo
        if sintoma_a and sintoma_a != "-- Seleccione el primer síntoma --":
            sintomas_b_filtrados = [s for s in sintomas_disponibles if s != sintoma_a]
            opciones_sintoma_b = ["-- Seleccione el segundo síntoma --"] + sintomas_b_filtrados
        else:
            opciones_sintoma_b = ["-- Primero seleccione el síntoma A --"]
        
        sintoma_b = st.selectbox(
            "Síntoma B:",
            opciones_sintoma_b,
            key="sintoma_b_select",
            help="Seleccione el segundo síntoma"
        )
    
    # Si se seleccionaron ambos síntomas
    if (sintoma_a and sintoma_a != "-- Seleccione el primer síntoma --" and
        sintoma_b and sintoma_b != "-- Seleccione el segundo síntoma --" and
        sintoma_b != "-- Primero seleccione el síntoma A --"):
        
        # Buscar resultados
        with st.spinner(f"🔍 Buscando especialidades para **{sintoma_a}** y **{sintoma_b}**..."):
            resultados = buscar_por_sintomas_local(sintoma_a, sintoma_b)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mostrar resultados
        if resultados:
            # Agrupar por especialidad para mostrar contador
            especialidades_unicas = list(set([r['especialidad'] for r in resultados]))
            
            st.markdown(f"""
            <div class="results-counter">
                <h4 style="margin: 0; color: #2E7D32;">
                    ✅ Se encontraron <strong>{len(resultados)} opciones</strong> 
                    en <strong>{len(especialidades_unicas)} especialidades</strong>
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🏥 Resultados de la búsqueda")
            
            # Mostrar cada resultado
            for resultado in resultados:
                mostrar_resultado_sintomas(resultado)
            
            # Información adicional
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; color: #666; padding: 1rem;'>
                <p>💡 <strong>Consejo:</strong> Estos resultados son orientativos. Te recomendamos consultar con el especialista para un diagnóstico preciso.</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
            <div class="no-results-especialidad">
                <h3 style="color: #FF6B6B; margin-bottom: 1rem;">😔 No se encontraron resultados</h3>
                <p style="font-size: 1.1rem; margin-bottom: 1rem;">
                    No hay especialidades u hospitales disponibles para la combinación de 
                    <strong>{sintoma_a}</strong> y <strong>{sintoma_b}</strong>
                </p>
                <p style="color: #888;">
                    • Intenta con otros síntomas<br>
                    • Considera buscar por especialidad directamente<br>
                    • Consulta con tu médico de cabecera
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Mostrar mensaje de ayuda
        st.info("👆 Selecciona dos síntomas diferentes para ver las especialidades y hospitales recomendados.")



# --- Estilos CSS ---
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .search-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .result-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .hospital-name {
        color: #0077b6;
        font-weight: bold;
        font-size: 18px;
    }
    .specialty-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header ---
st.markdown(
    """
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color: #0077b6; margin-bottom: 10px;'>🔍 Buscar Atención Médica</h1>
        <p style='color: #666; font-size: 18px;'>Encuentra el hospital y especialista que necesitas</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Inicializar estado de sesión ---
if "tipo_busqueda" not in st.session_state:
    st.session_state.tipo_busqueda = None

# --- Navegación ---
col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])

with col_nav2:
    if st.button("⬅️ Volver al Panel Principal", use_container_width=True):
        # Aquí deberías redirigir a tu página principal
        st.session_state.pantalla = "perfil"  # o como manejes la navegación
        st.switch_page("Inicio.py")  # Ajusta según tu estructura

# --- Contenido Principal ---
if st.session_state.tipo_busqueda is None:
    # Pantalla inicial de selección
    st.markdown(
        """
        <div class='search-container'>
            <h3 style='text-align: center; color: #023e8a; margin-bottom: 30px;'>
                ¿Cómo querés buscar atención médica?
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown(
                """
                <div class='search-container' style='text-align: center;'>
                    <h4 style='color: #0077b6;'>🏥 Por Especialidad</h4>
                    <p>Si ya sabés qué tipo de especialista necesitas</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Buscar por Especialidad", use_container_width=True, key="btn_especialidad"):
                st.session_state.tipo_busqueda = "especialidad"
                st.rerun()
    
    with col2:
        with st.container():
            st.markdown(
                """
                <div class='search-container' style='text-align: center;'>
                    <h4 style='color: #0077b6;'>🩺 Por Síntomas</h4>
                    <p>Si no estás seguro y querés que te ayudemos a encontrar la especialidad</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Buscar por Síntomas", use_container_width=True, key="btn_sintomas"):
                st.session_state.tipo_busqueda = "sintomas"
                st.rerun()

else:
    # Mostrar botón para volver al menú
    col_back, col_space = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Cambiar tipo de búsqueda"):
            st.session_state.tipo_busqueda = None
            st.rerun()
    
    # Mostrar la búsqueda correspondiente
    if st.session_state.tipo_busqueda == "especialidad":
        
        with st.container():
            st.markdown(
                """
                <div class='search-container'>
                """,
                unsafe_allow_html=True
            )
            buscar_por_especialidad()
            st.markdown("</div>", unsafe_allow_html=True)
    
    elif st.session_state.tipo_busqueda == "sintomas":
        with st.container():
            st.markdown(
                """
                <div class='search-container'>
                """,
                unsafe_allow_html=True
            )
            buscar_por_sintomas()
            st.markdown("</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; margin-top: 30px;'>
        <p>💙 InfoMed - Tu salud es nuestra prioridad</p>
    </div>
    """,
    unsafe_allow_html=True
)
