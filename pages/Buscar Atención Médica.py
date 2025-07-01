import streamlit as st
import sys
import os
import pandas as pd
import psycopg2
from geo_utils import geocode_address, haversine
import folium
from streamlit_folium import st_folium
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import execute_query, connect_to_supabase


# --- Page Configuration ---
st.set_page_config(
    page_title="InfoMed - Buscar Atención Médica",
    page_icon="🔍",
    layout="wide"
)

def solo_paciente_autenticado():
    """
    Permite el acceso solo si el usuario está autenticado y es paciente.
    Si no, muestra un mensaje y detiene la ejecución de la página.
    """
    # Verificar autenticación
    if "usuario_autenticado" not in st.session_state or st.session_state.usuario_autenticado is None:
        st.error("🔐 Debes iniciar sesión como paciente para acceder a esta página")
        if st.button("🏠 Ir a la página principal"):
            st.switch_page("Inicio.py")
        st.stop()
    
    # Verificar tipo de usuario
    if "tipo_usuario" not in st.session_state or st.session_state.tipo_usuario != "paciente":
        st.error("❌ Solo los pacientes pueden acceder a esta página.")
        if st.button("🔙 Volver al perfil"):
            st.switch_page("Inicio.py")
        st.stop()

# --- RESTRICCIÓN DE ACCESO ---
solo_paciente_autenticado()



def get_or_update_latlon_paciente(paciente_row, conn):
    if paciente_row.get('latitud') and paciente_row.get('longitud'):
        return paciente_row['latitud'], paciente_row['longitud']
    address = f"{paciente_row['calle']} {paciente_row['altura']}, {paciente_row['ciudad']}, {paciente_row['provincia']}, Argentina"
    lat, lon = geocode_address(address)
    if lat and lon:
        with conn.cursor() as cur:
            cur.execute("UPDATE paciente SET latitud=%s, longitud=%s WHERE id_paciente=%s", (lat, lon, paciente_row['id_paciente']))
            conn.commit()
        return lat, lon
    return None, None

def get_or_update_latlon_hospital(hospital_row, conn):
    if hospital_row.get('latitud') and hospital_row.get('longitud'):
        return hospital_row['latitud'], hospital_row['longitud']
    address = f"{hospital_row['calle']} {hospital_row['altura']}, {hospital_row['ciudad']}, {hospital_row['provincia']}, Argentina"
    lat, lon = geocode_address(address)
    if lat and lon:
        with conn.cursor() as cur:
            cur.execute("UPDATE hospital SET latitud=%s, longitud=%s WHERE id_hospital=%s", (lat, lon, hospital_row['id_hospital']))
            conn.commit()
        return lat, lon
    return None, None

def get_paciente_completo(id_paciente, conn):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT id_paciente, provincia, ciudad, calle, altura, latitud, longitud
            FROM paciente WHERE id_paciente = %s""", (id_paciente,)
        )
        row = cur.fetchone()
        if row:
            keys = ['id_paciente', 'provincia', 'ciudad', 'calle', 'altura', 'latitud', 'longitud']
            return dict(zip(keys, row))
        return None

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
        query = """
        SELECT DISTINCT h.id_hospital, h.desc_hospital, h.provincia, h.ciudad, h.calle, h.altura, h.telefono, h.latitud, h.longitud
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
        
        provincia = hospital.get('provincia', '')
        ciudad = hospital.get('ciudad', '')
        calle = hospital.get('calle', '')
        altura = hospital.get('altura', '')
        if provincia == ciudad:
            direccion = f"{provincia}, {calle} {altura}"
        else:
            direccion = f"{provincia}, {ciudad}, {calle} {altura}"
        if pd.isna(direccion) or direccion.strip(", ") == "":
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
            with st.spinner(f"🔍 Buscando hospitales para **{especialidad_seleccionada}**..."):
                hospitales = obtener_hospitales_por_especialidad(id_especialidad)
                if not hospitales.empty:
                    conn = connect_to_supabase()
                    # 2. Obtener paciente completo desde la base
                    paciente_id = st.session_state.usuario_autenticado['id_paciente']
                    paciente = get_paciente_completo(paciente_id, conn)
                    if not paciente:
                        st.error("No se pudo obtener la información de dirección del paciente.")
                        conn.close()
                        return
                    # 3. Obtener lat/lon del paciente
                    lat_pac, lon_pac = get_or_update_latlon_paciente(paciente, conn)
                    # 4. Para cada hospital, obtener/actualizar lat/lon y calcular distancia
                    hospitales['latitud'] = None
                    hospitales['longitud'] = None
                    hospitales['distancia_km'] = None
                    for idx, row in hospitales.iterrows():
                        lat, lon = get_or_update_latlon_hospital(row, conn)
                        hospitales.at[idx, 'latitud'] = lat
                        hospitales.at[idx, 'longitud'] = lon
                        if lat and lon and lat_pac and lon_pac:
                            hospitales.at[idx, 'distancia_km'] = haversine(lat_pac, lon_pac, lat, lon)
                        else:
                            hospitales.at[idx, 'distancia_km'] = float('inf')
                    # 5. Ordenar hospitales por distancia
                    hospitales = hospitales.sort_values('distancia_km')
                    # 6. Mostrar mapa con los 5 más cercanos
                    if lat_pac and lon_pac:
                        m = folium.Map(location=[lat_pac, lon_pac], zoom_start=13)
                        folium.Marker([lat_pac, lon_pac], tooltip="Tu casa", icon=folium.Icon(color="blue")).add_to(m)
                        for i, row in hospitales.head(5).iterrows():
                            if row['latitud'] and row['longitud']:
                                folium.Marker(
                                    [row['latitud'], row['longitud']],
                                    tooltip=row['desc_hospital'],
                                    popup=folium.Popup(f"{row['ciudad']}<br>{row['calle']} {row['altura']}", max_width=400),
                                    icon=folium.Icon(color="red")
                                ).add_to(m)
                        st_folium(m, width=700, height=400)
                    else:
                        st.warning("No se pudo determinar la ubicación del paciente para mostrar el mapa.")
                    # 7. Mostrar listado ordenado (pero por distancia)
                    st.markdown(f"""
                    <div class="results-counter" style="margin-top: 1rem; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: #2E7D32;">
                            ✅ Se encontraron <strong>{len(hospitales)} hospitales</strong> 
                            que ofrecen <strong>{especialidad_seleccionada}</strong>
                        </h4>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("### 🏥 Resultados de la búsqueda (ordenados por cercanía)")
                    for idx, hospital in hospitales.iterrows():
                        st.markdown(f"<div style='color:#888; font-size:0.95rem;'>Distancia: {hospital['distancia_km']:.2f} km</div>", unsafe_allow_html=True)
                        mostrar_hospital_card(hospital)
                    st.markdown("---")
                    st.markdown("""
                    <div style='text-align: center; color: #666; padding: 1rem;'>
                        <p>💡 <strong>Consejo:</strong> Te recomendamos llamar antes de concurrir para confirmar horarios y disponibilidad.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    conn.close()
        else:
            st.error("❌ No se pudo obtener el ID de la especialidad seleccionada.")
    
    else:
        # Mostrar mensaje de ayuda cuando no hay selección
        st.info("👆 Selecciona una especialidad médica del menú desplegable para ver los hospitales disponibles.")

def buscar_por_sintomas(sintoma_a, sintoma_b):
    """
    Busca especialidades y hospitales basados en dos síntomas dados.
    Busca tanto por especialidad como por atención directa de patología.
    
    Args:
        sintoma_a (str): Descripción del primer síntoma
        sintoma_b (str): Descripción del segundo síntoma
    
    Returns:
        list: Lista de diccionarios con especialidad, hospital, dirección y teléfono
    """
    
    query = """
    -- Buscar hospitales por especialidad (patología -> especialidad -> hospital)
    SELECT DISTINCT 
        e.desc_especialidad as especialidad,
        h.desc_hospital as hospital,
        h.provincia,
        h.ciudad,
        h.calle,
        h.altura,
        h.telefono,
        'Por Especialidad' as tipo_atencion
    FROM patologia p
    INNER JOIN sintoma s1 ON (p.id_sintoma_1 = s1.id_sintoma OR p.id_sintoma_2 = s1.id_sintoma)
    INNER JOIN sintoma s2 ON (p.id_sintoma_1 = s2.id_sintoma OR p.id_sintoma_2 = s2.id_sintoma)
    INNER JOIN patologia_especialidades pe ON p.id_patologia = pe.id_patologia
    INNER JOIN especialidades e ON pe.id_especialidad = e.id_especialidad
    INNER JOIN hospital_especialidades he ON e.id_especialidad = he.id_especialidad
    INNER JOIN hospital h ON he.id_hospital = h.id_hospital
    WHERE s1.desc_sintoma = %s 
      AND s2.desc_sintoma = %s
      AND s1.id_sintoma != s2.id_sintoma
    
    UNION
    
    -- Buscar hospitales que atienden la patología directamente
    SELECT DISTINCT 
        CONCAT('Atención directa: ', p.desc_patologia) as especialidad,
        h.desc_hospital as hospital,
        h.provincia,
        h.ciudad,
        h.calle,
        h.altura,
        h.telefono,
        'Por Patología' as tipo_atencion
    FROM patologia p
    INNER JOIN sintoma s1 ON (p.id_sintoma_1 = s1.id_sintoma OR p.id_sintoma_2 = s1.id_sintoma)
    INNER JOIN sintoma s2 ON (p.id_sintoma_1 = s2.id_sintoma OR p.id_sintoma_2 = s2.id_sintoma)
    INNER JOIN patologia_hospital ph ON p.id_patologia = ph.id_patologia
    INNER JOIN hospital h ON ph.id_hospital = h.id_hospital
    WHERE s1.desc_sintoma = %s 
      AND s2.desc_sintoma = %s
      AND s1.id_sintoma != s2.id_sintoma
    
    ORDER BY especialidad, hospital;
    """
    
    try:
        # Ejecutar la consulta con parámetros para ambas partes del UNION
        df_results = execute_query(query, params=(sintoma_a, sintoma_b, sintoma_a, sintoma_b))
        
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
        """Busca especialidades y hospitales basados en dos síntomas dados - VERSIÓN COMPLETA"""
        query = """
        -- Buscar hospitales por especialidad (patología -> especialidad -> hospital)
        SELECT DISTINCT 
            e.desc_especialidad as especialidad,
            h.desc_hospital as hospital,
            h.provincia,
            h.ciudad,
            h.calle,
            h.altura,
            h.telefono,
            'Por Especialidad' as tipo_atencion
        FROM patologia p
        INNER JOIN sintoma s1 ON (p.id_sintoma_1 = s1.id_sintoma OR p.id_sintoma_2 = s1.id_sintoma)
        INNER JOIN sintoma s2 ON (p.id_sintoma_1 = s2.id_sintoma OR p.id_sintoma_2 = s2.id_sintoma)
        INNER JOIN patologia_especialidades pe ON p.id_patologia = pe.id_patologia
        INNER JOIN especialidades e ON pe.id_especialidad = e.id_especialidad
        INNER JOIN hospital_especialidades he ON e.id_especialidad = he.id_especialidad
        INNER JOIN hospital h ON he.id_hospital = h.id_hospital
        WHERE (
            (s1.desc_sintoma = %s AND s2.desc_sintoma = %s) OR 
            (s1.desc_sintoma = %s AND s2.desc_sintoma = %s)
        )
        AND s1.id_sintoma != s2.id_sintoma
        
        UNION
        
        -- Buscar hospitales que atienden la patología directamente
        SELECT DISTINCT 
            CONCAT('Atención directa: ', p.desc_patologia) as especialidad,
            h.desc_hospital as hospital,
            h.provincia,
            h.ciudad,
            h.calle,
            h.altura,
            h.telefono,
            'Por Patología' as tipo_atencion
        FROM patologia p
        INNER JOIN sintoma s1 ON (p.id_sintoma_1 = s1.id_sintoma OR p.id_sintoma_2 = s1.id_sintoma)
        INNER JOIN sintoma s2 ON (p.id_sintoma_1 = s2.id_sintoma OR p.id_sintoma_2 = s2.id_sintoma)
        INNER JOIN patologia_hospital ph ON p.id_patologia = ph.id_patologia
        INNER JOIN hospital h ON ph.id_hospital = h.id_hospital
        WHERE (
            (s1.desc_sintoma = %s AND s2.desc_sintoma = %s) OR 
            (s1.desc_sintoma = %s AND s2.desc_sintoma = %s)
        )
        AND s1.id_sintoma != s2.id_sintoma
        
        ORDER BY especialidad, hospital;
        """
        
        try:
            # Pasar los parámetros para ambas partes del UNION: (A,B,B,A) + (A,B,B,A)
            df_results = execute_query(query, params=(sintoma_a, sintoma_b, sintoma_b, sintoma_a, 
                                                    sintoma_a, sintoma_b, sintoma_b, sintoma_a))
            if not df_results.empty:
                return df_results.to_dict('records')
            else:
                return []
        except Exception as e:
            st.error(f"Error en la búsqueda: {str(e)}")
            return []

    def mostrar_resultado_sintomas(resultado):
        """Muestra una tarjeta de resultado con especialidad y hospital"""
        provincia = resultado.get('provincia', '')
        ciudad = resultado.get('ciudad', '')
        calle = resultado.get('calle', '')
        altura = resultado.get('altura', '')
        if provincia == ciudad:
            direccion = f"{provincia}, {calle} {altura}"
        else:
            direccion = f"{provincia}, {ciudad}, {calle} {altura}"
        if pd.isna(direccion) or direccion.strip(", ") == "":
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
        st.error("❌ No se pudieron cargar los síntomas.")
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
        
        with st.spinner(f"🔍 Buscando especialidades para **{sintoma_a}** y **{sintoma_b}**..."):
            resultados = buscar_por_sintomas_local(sintoma_a, sintoma_b)
        
        if resultados:
            import pandas as pd
            import folium
            from streamlit_folium import st_folium
            from geo_utils import haversine
            from functions import connect_to_supabase
            conn = connect_to_supabase()
            # 2. Obtener paciente completo desde la base
            paciente_id = st.session_state.usuario_autenticado['id_paciente']
            paciente = get_paciente_completo(paciente_id, conn)
            if not paciente:
                st.error("No se pudo obtener la información de dirección del paciente.")
                conn.close()
                return
            lat_pac, lon_pac = get_or_update_latlon_paciente(paciente, conn)
            # 3. Convertir resultados a DataFrame para facilitar el manejo
            df_resultados = pd.DataFrame(resultados)
            # 4. Para cada hospital, obtener/actualizar lat/lon y calcular distancia
            df_resultados['latitud'] = None
            df_resultados['longitud'] = None
            df_resultados['distancia_km'] = None
            # Necesitamos el id_hospital para actualizar, pero los resultados no lo traen
            # Así que buscamos el hospital por nombre para obtener el id y actualizar lat/lon
            for idx, row in df_resultados.iterrows():
                # Buscar hospital por nombre exacto
                cur = conn.cursor()
                cur.execute("SELECT id_hospital, latitud, longitud, calle, altura, ciudad, provincia FROM hospital WHERE desc_hospital = %s LIMIT 1", (row['hospital'],))
                h = cur.fetchone()
                if h:
                    id_hospital, lat, lon, calle, altura, ciudad, provincia = h
                    if not lat or not lon:
                        # Geocodificar si falta
                        address = f"{calle} {altura}, {ciudad}, {provincia}, Argentina"
                        lat, lon = geocode_address(address)
                        if lat and lon:
                            cur.execute("UPDATE hospital SET latitud=%s, longitud=%s WHERE id_hospital=%s", (lat, lon, id_hospital))
                            conn.commit()
                    df_resultados.at[idx, 'latitud'] = lat
                    df_resultados.at[idx, 'longitud'] = lon
                    if lat and lon and lat_pac and lon_pac:
                        df_resultados.at[idx, 'distancia_km'] = haversine(lat_pac, lon_pac, lat, lon)
                    else:
                        df_resultados.at[idx, 'distancia_km'] = float('inf')
                else:
                    df_resultados.at[idx, 'distancia_km'] = float('inf')
            # 5. Ordenar por distancia
            df_resultados = df_resultados.sort_values('distancia_km')
            # 6. Mostrar mapa con los 5 más cercanos
            if lat_pac and lon_pac:
                m = folium.Map(location=[lat_pac, lon_pac], zoom_start=13)
                folium.Marker([lat_pac, lon_pac], tooltip="Tu casa",
                            icon=folium.Icon(color="blue")).add_to(m)
                for i, row in df_resultados.head(5).iterrows():
                    if row['latitud'] and row['longitud']:
                        folium.Marker(
                            [row['latitud'], row['longitud']],
                            tooltip=row['hospital'],
                            popup=folium.Popup(f"{row['ciudad']}<br>{row['calle']} {row['altura']}", max_width=400),
                            icon=folium.Icon(color="red")
                        ).add_to(m)
                        
                # Mostrar el mapa
                st_folium(m, width=700, height=400)
                
                # CSS mejorado para mantener espaciado natural
                st.markdown("""
                <style>
                /* Solo reducir ligeramente el margen inferior del mapa */
                iframe[src*="folium"] {
                    margin-bottom: 0.5rem !important;
                }
                
                /* Mantener espaciado normal entre elementos */
                .stVerticalBlock {
                    gap: 1rem !important;
                }
                
                /* Asegurar que las tarjetas tengan su espaciado normal */
                div[data-testid="stVerticalBlock"] > div {
                    margin: 0.5rem 0 !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
            else:
                st.warning("No se pudo determinar la ubicación del paciente para mostrar el mapa.")
            # Resto del código sin cambios...

            st.markdown("### 🏥 Resultados de la búsqueda (ordenados por cercanía)")
            for idx, resultado in df_resultados.iterrows():
                st.markdown(f"<div style='color:#888; font-size:0.95rem;'>Distancia: {resultado['distancia_km']:.2f} km</div>", unsafe_allow_html=True)
                mostrar_resultado_sintomas(resultado)
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; color: #666; padding: 1rem;'>
                <p>💡 <strong>Consejo:</strong> Estos resultados son orientativos. Te recomendamos consultar con el especialista para un diagnóstico preciso.</p>
            </div>
            """, unsafe_allow_html=True)
            conn.close()
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
    iframe, .folium-map, .st-folium {
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
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
            
            buscar_por_especialidad()
            st.markdown("</div>", unsafe_allow_html=True)
    
    elif st.session_state.tipo_busqueda == "sintomas":
        with st.container():
            buscar_por_sintomas()
            st.markdown("</div>", unsafe_allow_html=True)

# Botón para volver al perfil
if st.button("🔙 Volver al perfil"):
    st.switch_page("Inicio.py")

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