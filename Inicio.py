import streamlit as st  
import functions as f
from datetime import date

# Utilidad para mostrar dirección sin repetir provincia y ciudad

def formatear_direccion(provincia, ciudad, calle, altura):
    if provincia and ciudad and provincia.strip().lower() == ciudad.strip().lower():
        return f"{provincia}, {calle}, {altura}"
    else:
        return f"{provincia}, {ciudad}, {calle}, {altura}"

min_date = date(1900, 1, 1)  # Fecha mínima (ajustar a tus necesidades)
max_date = date(2100, 12, 31)  # Fecha máxima (ajustar a tus necesidades)

# Opciones de obra social
OBRAS_SOCIALES = ["Seleccionar...", "OSDE", "PAMI", "Swiss Medical", "Galeno", "Medicus"]

def registrar_usuario(dni, apellido, nombre, fecha_de_nacimiento, sexo, provincia, ciudad, calle, altura, obra_social, correo, contraseña):
    """
    Registra un nuevo usuario/paciente en la tabla paciente.
    
    Args:
        dni (str): DNI del paciente (usado como id_paciente)
        apellido (str): Apellido del paciente
        nombre (str): Nombre del paciente
        fecha_de_nacimiento (str/date): Fecha de nacimiento
        sexo (str): Sexo del paciente
        provincia (str): Provincia del paciente
        ciudad (str): Cuidad del paciente
        calle (str): Calle del paciente
        altura (str): Altura de la calle del paciente
        obra_social (str): Obra social del paciente
        correo (str): Email del paciente
        contraseña (str): Contraseña del paciente
        
    Returns:
        dict: {'success': True/False, 'error': mensaje} según el resultado
    """
    try:
        # Validar si ya existe un paciente con ese DNI
        query_check = "SELECT 1 FROM paciente WHERE id_paciente = %s"
        existe = f.execute_query(query_check, params=(dni,), is_select=True)
        if not existe.empty:
            return {'success': False, 'error': 'Ya existe una cuenta con este DNI, revise sus datos'}
        
        query = """
            INSERT INTO paciente (
                id_paciente, apellido, nombre, fecha_de_nacimiento,
                sexo, provincia, ciudad, calle, altura, obra_social,
                email, contraseña
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dni, apellido, nombre, fecha_de_nacimiento,
            sexo, provincia, ciudad, calle, altura, obra_social,
            correo, contraseña
        )
        
        resultado = f.execute_query(query, params=params, is_select=False)
        
        if resultado:
            print(f"Usuario {nombre} {apellido} registrado exitosamente.")
            return {'success': True}
        else:
            print(f"Error al registrar el usuario {nombre} {apellido}.")
            return {'success': False, 'error': 'Error al registrar el usuario'}
            
    except Exception as e:
        print(f"Error en registrar_usuario: {e}")
        return {'success': False, 'error': str(e)}

def registrar_medico(dni, apellido, nombre, sexo, id_hospital=None, telefono=None, correo=None, contraseña=None):
    """
    Registra un nuevo usuario/medico en la tabla medico.
    
    Args:
        dni (str): DNI del medico (usado como id_medico)
        apellido (str): Apellido del medico
        nombre (str): Nombre del medico
        sexo (str): Sexo del medico
        id_hospital (int, optional): ID del hospital. Puede ser None/NULL
        telefono (str, optional): Teléfono del medico. Puede ser None/NULL
        correo (str, optional): Email del medico. Puede ser None/NULL
        contraseña (str, optional): Contraseña del medico. Puede ser None/NULL
        
    Returns:
        dict: {'success': True/False, 'error': mensaje} según el resultado
    """
    try:
        # Validar si ya existe un médico con ese DNI
        query_check = "SELECT 1 FROM medico WHERE id_medico = %s"
        existe = f.execute_query(query_check, params=(dni,), is_select=True)
        if not existe.empty:
            return {'success': False, 'error': 'Ya existe una cuenta con este DNI, revise sus datos'}
        
        query = """
            INSERT INTO medico (
                id_medico, apellido, nombre,
                sexo, id_hospital, telefono,
                email, contraseña
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dni, apellido, nombre,
            sexo, id_hospital, telefono,
            correo, contraseña
        )
        
        resultado = f.execute_query(query, params=params, is_select=False)
        
        if resultado:
            print(f"Usuario {nombre} {apellido} registrado exitosamente.")
            return {'success': True}
        else:
            print(f"Error al registrar el usuario {nombre} {apellido}.")
            return {'success': False, 'error': 'Error al registrar el usuario'}
            
    except Exception as e:
        print(f"Error en registrar_usuario: {e}")
        return {'success': False, 'error': str(e)}
    
# functions.py - Funciones para manejo de hospitales usando PostgreSQL directo

import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'aws-0-us-east-1.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.ihguxvmtprnyhyhstvdp',
    'password': 'Csdatos2025!'
}

def get_db_connection():
    """Obtiene una conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def obtener_hospitales_existentes():
    """
    Obtiene todos los hospitales existentes en la base de datos
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM hospital ORDER BY desc_hospital")
            
            # Obtener nombres de columnas
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            hospitales = []
            for row in rows:
                hospitales.append(dict(zip(columns, row)))
            
            return hospitales
            
    except Exception as e:
        print(f"Error en obtener_hospitales_existentes: {e}")
        return []
    finally:
        conn.close()

def buscar_hospital_por_nombre(nombre_hospital):
    """
    Busca un hospital por su nombre exacto (case insensitive)
    Retorna los datos del hospital si existe, None si no existe
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            # Búsqueda case-insensitive
            cursor.execute(
                "SELECT * FROM hospital WHERE LOWER(desc_hospital) = LOWER(%s)",
                (nombre_hospital.strip(),)
            )
            
            row = cursor.fetchone()
            
            if row:
                # Obtener nombres de columnas
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            else:
                return None
                
    except Exception as e:
        print(f"Error en buscar_hospital_por_nombre: {e}")
        return None
    finally:
        conn.close()

def buscar_hospitales_similares(termino_busqueda, limite=5):
    """
    Busca hospitales que contengan el término de búsqueda
    Útil para mostrar sugerencias al usuario
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM hospital 
                WHERE LOWER(desc_hospital) LIKE LOWER(%s) 
                ORDER BY desc_hospital 
                LIMIT %s
            """, (f"%{termino_busqueda.strip()}%", limite))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            hospitales = []
            for row in rows:
                hospitales.append(dict(zip(columns, row)))
            
            return hospitales
            
    except Exception as e:
        print(f"Error en buscar_hospitales_similares: {e}")
        return []
    finally:
        conn.close()

def agregar_nuevo_hospital(nombre, provincia, ciudad, calle, altura, telefono):
    """
    Agrega un nuevo hospital a la base de datos
    Retorna el hospital creado con su ID generado automáticamente
    """
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'No se pudo conectar a la base de datos'}
    
    try:
        with conn.cursor() as cursor:
            # Primero verificar si necesitamos configurar la secuencia
            cursor.execute("""
                SELECT column_default 
                FROM information_schema.columns 
                WHERE table_name = 'hospital' AND column_name = 'id_hospital'
            """)
            
            default_info = cursor.fetchone()
            
            # Si no tiene secuencia autoincremental, obtener el próximo ID manualmente
            if not default_info or not default_info[0] or 'nextval' not in str(default_info[0]):
                cursor.execute("SELECT COALESCE(MAX(id_hospital), 0) + 1 FROM hospital")
                next_id = cursor.fetchone()[0]
                
                # Insertar con ID específico
                cursor.execute("""
                    INSERT INTO hospital (id_hospital, desc_hospital, provincia, ciudad, calle, altura, telefono) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s) 
                    RETURNING *
                """, (next_id, nombre.strip(), provincia.strip(), ciudad.strip(), calle.strip(), altura.strip(), telefono.strip()))
            else:
                # La tabla tiene secuencia, insertar normalmente
                cursor.execute("""
                    INSERT INTO hospital (desc_hospital, provincia, ciudad, calle, altura, telefono) 
                    VALUES (%s, %s, %s, %s, %s, %s) 
                    RETURNING *
                """, (nombre.strip(), provincia.strip(), ciudad.strip(), calle.strip(), altura.strip(), telefono.strip()))
            
            # Obtener el hospital recién creado
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            hospital = dict(zip(columns, row))
            
            conn.commit()
            
            return {
                'success': True,
                'hospital': hospital
            }
            
    except Exception as e:
        conn.rollback()
        print(f"Error en agregar_nuevo_hospital: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

def obtener_o_crear_hospital(nombre, provincia=None, ciudad=None, calle=None, altura=None, telefono=None):
    """
    Busca un hospital por nombre. Si no existe, lo crea con los datos proporcionados.
    Retorna el hospital (existente o nuevo) con su ID
    """
    try:
        # Primero buscar si el hospital existe
        hospital_existente = buscar_hospital_por_nombre(nombre)
        
        if hospital_existente:
            return {
                'success': True,
                'hospital': hospital_existente,
                'es_nuevo': False
            }
        
        # Si no existe, crear uno nuevo
        if not provincia or not ciudad or not calle or not altura or not telefono:
            return {
                'success': False,
                'error': 'Se requieren provincia, ciudad, calle, altura y teléfono para crear un nuevo hospital'
            }
        
        resultado_nuevo = agregar_nuevo_hospital(nombre, provincia, ciudad, calle, altura, telefono)
        
        if resultado_nuevo['success']:
            return {
                'success': True,
                'hospital': resultado_nuevo['hospital'],
                'es_nuevo': True
            }
        else:
            return resultado_nuevo
            
    except Exception as e:
        print(f"Error en obtener_o_crear_hospital: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def registrar_medico_con_hospital(dni, apellido, nombre, sexo, nombre_hospital, 
                                provincia_hospital=None, ciudad_hospital=None, calle_hospital=None, altura_hospital=None, telefono_hospital=None,
                                telefono_medico=None, correo=None, contraseña=None):
    """
    Registra un médico y maneja la lógica del hospital (crear o usar existente)
    """
    try:
        # Paso 1: Obtener o crear el hospital
        resultado_hospital = obtener_o_crear_hospital(
            nombre=nombre_hospital,
            provincia=provincia_hospital,
            ciudad=ciudad_hospital,
            calle=calle_hospital,
            altura=altura_hospital,
            telefono=telefono_hospital
        )
        
        if not resultado_hospital['success']:
            return {
                'success': False,
                'mensaje': f"Error con el hospital: {resultado_hospital['error']}"
            }
        
        hospital = resultado_hospital['hospital']
        id_hospital = hospital['id_hospital']
        
        # Paso 2: Registrar el médico usando la función con validación
        resultado_medico = registrar_medico(
            dni=dni,
            apellido=apellido,
            nombre=nombre,
            sexo=sexo,
            id_hospital=id_hospital,
            telefono=telefono_medico,
            correo=correo,
            contraseña=contraseña
        )
        if resultado_medico['success']:
            return {
                'success': True,
                'medico': {
                    'id_medico': dni,
                    'apellido': apellido,
                    'nombre': nombre,
                    'sexo': sexo,
                    'id_hospital': id_hospital,
                    'telefono': telefono_medico,
                    'email': correo
                },
                'datos_hospital': hospital,
                'hospital_nuevo': resultado_hospital['es_nuevo']
            }
        else:
            return {
                'success': False,
                'mensaje': resultado_medico.get('error', 'Error desconocido')
            }
    except Exception as e:
        print(f"Error en registrar_medico_con_hospital: {e}")
        return {
            'success': False,
            'mensaje': str(e)
        }

def configurar_secuencia_hospital():
    """
    Configura la secuencia autoincremental para la tabla hospital si no existe
    """
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'No se pudo conectar a la base de datos'}
    
    try:
        with conn.cursor() as cursor:
            # Verificar si ya existe una secuencia
            cursor.execute("""
                SELECT column_default 
                FROM information_schema.columns 
                WHERE table_name = 'hospital' AND column_name = 'id_hospital'
            """)
            
            default_info = cursor.fetchone()
            
            # Si no tiene secuencia, crearla
            if not default_info or not default_info[0] or 'nextval' not in str(default_info[0]):
                
                # Obtener el valor máximo actual
                cursor.execute("SELECT COALESCE(MAX(id_hospital), 0) FROM hospital")
                max_id = cursor.fetchone()[0]
                
                # Crear secuencia
                cursor.execute(f"""
                    CREATE SEQUENCE IF NOT EXISTS hospital_id_hospital_seq 
                    START WITH {max_id + 1} 
                    INCREMENT BY 1 
                    NO MINVALUE 
                    NO MAXVALUE 
                    CACHE 1
                """)
                
                # Configurar la columna para usar la secuencia
                cursor.execute("""
                    ALTER TABLE ONLY hospital 
                    ALTER COLUMN id_hospital SET DEFAULT nextval('hospital_id_hospital_seq'::regclass)
                """)
                
                # Establecer la secuencia como propiedad de la columna
                cursor.execute("""
                    ALTER SEQUENCE hospital_id_hospital_seq 
                    OWNED BY hospital.id_hospital
                """)
                
                conn.commit()
                
                return {
                    'success': True,
                    'mensaje': f'Secuencia configurada correctamente. Próximo ID: {max_id + 1}'
                }
            else:
                return {
                    'success': True,
                    'mensaje': 'La secuencia ya estaba configurada'
                }
                
    except Exception as e:
        conn.rollback()
        print(f"Error en configurar_secuencia_hospital: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

def verificar_configuracion_hospital():
    """
    Verifica la configuración de la tabla hospital
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, column_default, is_nullable, data_type
                FROM information_schema.columns 
                WHERE table_name = 'hospital' AND column_name = 'id_hospital'
            """)
            
            row = cursor.fetchone()
            if row:
                print(f"Configuración id_hospital: {row}")
                return True
            else:
                print("La columna id_hospital no existe")
                return False
                
    except Exception as e:
        print(f"Error verificando configuración: {e}")
        return False
    finally:
        conn.close()

def autenticar_paciente(email, contraseña):
    """
    Autentica un paciente usando email y contraseña
    """
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'No se pudo conectar a la base de datos'}
    
    try:
        with conn.cursor() as cursor:
            # Debug: Verificar que la tabla existe y tiene datos
            cursor.execute("SELECT COUNT(*) FROM paciente")
            total_pacientes = cursor.fetchone()[0]
            print(f"Total de pacientes en la base de datos: {total_pacientes}")
            
            # Buscar el usuario específico
            cursor.execute("""
                SELECT * FROM paciente 
                WHERE email = %s AND contraseña = %s
            """, (email, contraseña))
            
            row = cursor.fetchone()
            
            if row:
                # Obtener nombres de columnas
                columns = [desc[0] for desc in cursor.description]
                paciente = dict(zip(columns, row))
                print(f"Paciente autenticado exitosamente: {paciente['nombre']} {paciente['apellido']}")
                
                return {
                    'success': True,
                    'usuario': paciente,
                    'tipo': 'paciente'
                }
            else:
                print(f"Autenticación fallida para email: {email}")
                return {
                    'success': False,
                    'error': 'Email o contraseña incorrectos'
                }
                
    except Exception as e:
        print(f"Error en autenticar_paciente: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

def autenticar_medico(email, contraseña):
    """
    Autentica un médico usando email y contraseña
    """
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'No se pudo conectar a la base de datos'}
    
    try:
        with conn.cursor() as cursor:
            # Debug: Verificar que la tabla existe y tiene datos
            cursor.execute("SELECT COUNT(*) FROM medico")
            total_medicos = cursor.fetchone()[0]
            print(f"Total de médicos en la base de datos: {total_medicos}")
            
            # Buscar el usuario específico
            cursor.execute("""
                SELECT m.*, h.desc_hospital 
                FROM medico m 
                LEFT JOIN hospital h ON m.id_hospital = h.id_hospital
                WHERE m.email = %s AND m.contraseña = %s
            """, (email, contraseña))
            
            row = cursor.fetchone()
            
            if row:
                # Obtener nombres de columnas
                columns = [desc[0] for desc in cursor.description]
                medico = dict(zip(columns, row))
                print(f"Médico autenticado exitosamente: {medico['nombre']} {medico['apellido']}")
                
                return {
                    'success': True,
                    'usuario': medico,
                    'tipo': 'medico'
                }
            else:
                print(f"Autenticación fallida para email: {email}")
                return {
                    'success': False,
                    'error': 'Email o contraseña incorrectos'
                }
                
    except Exception as e:
        print(f"Error en autenticar_medico: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

def autenticar_usuario(email, contraseña, tipo_usuario):
    """
    Autentica un usuario según su tipo (paciente o médico) usando email
    """
    if tipo_usuario == "paciente":
        return autenticar_paciente(email, contraseña)
    elif tipo_usuario == "medico":
        return autenticar_medico(email, contraseña)
    else:
        return {
            'success': False,
            'error': 'Tipo de usuario no válido'
        }

def verificar_usuario_existente(email):
    """
    Verifica si un email ya está registrado como paciente o médico
    Retorna información sobre el tipo de usuario existente
    """
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'No se pudo conectar a la base de datos'}
    
    try:
        with conn.cursor() as cursor:
            # Verificar si existe como paciente
            cursor.execute("SELECT id_paciente, nombre, apellido FROM paciente WHERE email = %s", (email,))
            paciente = cursor.fetchone()
            
            # Verificar si existe como médico
            cursor.execute("SELECT id_medico, nombre, apellido FROM medico WHERE email = %s", (email,))
            medico = cursor.fetchone()
            
            if paciente and medico:
                return {
                    'success': True,
                    'existe': True,
                    'tipo_existente': 'ambos',
                    'mensaje': f'El email {email} está registrado tanto como paciente como médico. Contacta al administrador.',
                    'paciente': {'nombre': paciente[1], 'apellido': paciente[2]},
                    'medico': {'nombre': medico[1], 'apellido': medico[2]}
                }
            elif paciente:
                return {
                    'success': True,
                    'existe': True,
                    'tipo_existente': 'paciente',
                    'mensaje': f'El email {email} ya está registrado como paciente.',
                    'usuario': {'nombre': paciente[1], 'apellido': paciente[2]}
                }
            elif medico:
                return {
                    'success': True,
                    'existe': True,
                    'tipo_existente': 'medico',
                    'mensaje': f'El email {email} ya está registrado como médico.',
                    'usuario': {'nombre': medico[1], 'apellido': medico[2]}
                }
            else:
                return {
                    'success': True,
                    'existe': False,
                    'mensaje': 'Email no registrado'
                }
                
    except Exception as e:
        print(f"Error en verificar_usuario_existente: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

def autenticar_usuario_con_verificacion(email, contraseña, tipo_usuario):
    """
    Autentica un usuario verificando primero si existe como otro tipo
    """
    # Primero verificar si el usuario existe como otro tipo
    verificacion = verificar_usuario_existente(email)
    
    if not verificacion['success']:
        return verificacion
    
    if verificacion['existe']:
        tipo_existente = verificacion['tipo_existente']
        
        # Si existe como ambos tipos, mostrar error
        if tipo_existente == 'ambos':
            return {
                'success': False,
                'error': verificacion['mensaje'],
                'tipo_conflicto': 'ambos'
            }
        
        # Si existe como un tipo diferente al que está intentando autenticar
        if tipo_existente != tipo_usuario:
            return {
                'success': False,
                'error': f"❌ {verificacion['mensaje']} Si intentas acceder como {'paciente' if tipo_usuario == 'medico' else 'médico'}, por favor selecciona el tipo correcto.",
                'tipo_conflicto': tipo_existente,
                'usuario_existente': verificacion['usuario']
            }
    
    # Si no hay conflicto, proceder con la autenticación normal
    return autenticar_usuario(email, contraseña, tipo_usuario)

def verificar_autenticacion():
    """
    Verifica si el usuario está autenticado
    Retorna True si está autenticado, False en caso contrario
    """
    return "usuario_autenticado" in st.session_state and st.session_state.usuario_autenticado is not None

def mostrar_menu_navegacion():
    """
    Muestra el menú de navegación con las páginas disponibles según el tipo de usuario
    """
    if not verificar_autenticacion():
        st.warning("🔐 Debes iniciar sesión para acceder a las páginas")
        return
    
    tipo_usuario = st.session_state.tipo_usuario
    
    st.markdown("---")
    st.subheader("🧭 Navegación")
    
    # Páginas disponibles según el tipo de usuario
    if tipo_usuario == "paciente":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Buscar Atención Médica", use_container_width=True):
                st.switch_page("pages/Buscar Atención Médica.py")
        with col2:
            if st.button("📋 Ver mis Estudios", use_container_width=True):
                st.switch_page("pages/Ver mis Estudios.py")
    
    elif tipo_usuario == "medico":
        if st.button("📤 Cargar Nuevo Estudio", use_container_width=True):
            st.switch_page("pages/Cargar Nuevo Estudio.py")

def actualizar_paciente(dni, apellido, nombre, fecha_de_nacimiento, sexo, provincia, ciudad, calle, altura, obra_social, correo, contraseña):
    """
    Actualiza la información de un paciente en la base de datos
    """
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'No se pudo conectar a la base de datos'}
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE paciente 
                SET apellido = %s, nombre = %s, fecha_de_nacimiento = %s,
                    sexo = %s, provincia = %s, ciudad = %s, calle = %s, altura = %s,
                    obra_social = %s, email = %s, contraseña = %s
                WHERE id_paciente = %s
                RETURNING *
            """, (apellido, nombre, fecha_de_nacimiento, sexo, provincia, ciudad, calle, altura, obra_social, correo, contraseña, dni))
            
            row = cursor.fetchone()
            
            if row:
                # Obtener nombres de columnas
                columns = [desc[0] for desc in cursor.description]
                paciente_actualizado = dict(zip(columns, row))
                
                conn.commit()
                
                return {
                    'success': True,
                    'usuario': paciente_actualizado,
                    'mensaje': 'Perfil actualizado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se encontró el paciente'
                }
                
    except Exception as e:
        conn.rollback()
        print(f"Error en actualizar_paciente: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

def actualizar_medico(dni, apellido, nombre, sexo, id_hospital, telefono, correo, contraseña):
    """
    Actualiza la información de un médico en la base de datos
    """
    conn = get_db_connection()
    if not conn:
        return {'success': False, 'error': 'No se pudo conectar a la base de datos'}
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE medico 
                SET apellido = %s, nombre = %s, sexo = %s, id_hospital = %s,
                    telefono = %s, email = %s, contraseña = %s
                WHERE id_medico = %s
                RETURNING *
            """, (apellido, nombre, sexo, id_hospital, telefono, correo, contraseña, dni))
            
            row = cursor.fetchone()
            
            if row:
                # Obtener nombres de columnas
                columns = [desc[0] for desc in cursor.description]
                medico_actualizado = dict(zip(columns, row))
                
                conn.commit()
                
                return {
                    'success': True,
                    'usuario': medico_actualizado,
                    'mensaje': 'Perfil actualizado exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se encontró el médico'
                }
                
    except Exception as e:
        conn.rollback()
        print(f"Error en actualizar_medico: {e}")
        return {
            'success': False,
            'error': str(e)
        }
    finally:
        conn.close()

def obtener_hospital_por_id(id_hospital):
    """
    Obtiene la información de un hospital por su ID
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM hospital WHERE id_hospital = %s", (id_hospital,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            else:
                return None
                
    except Exception as e:
        print(f"Error en obtener_hospital_por_id: {e}")
        return None
    finally:
        conn.close()

################################## aca empieza la UI



# --- Page Configuration (Optional but Recommended) ---
st.set_page_config(
    page_title="InfoMed - Login",
    page_icon="🏥",
    layout="centered" # "wide" or "centered"
)

# --- Main Application ---
st.markdown(
    """
    <h1 style='text-align: center; color: #000000; font-size: 45px; font-weight: bold;'>
        ¡Bienvenido a InfoMed!
    </h1>
    """,
    unsafe_allow_html=True
)

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
    <h1 style='font-size: 36px; color: 	#0077b6; text-align: center;'>
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

st.markdown(
    """
    <h1 style='margin-bottom: 20px'
    """,
    unsafe_allow_html=True
)

if st.session_state.pantalla is None:
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col3:
        st.image("C:/Users/trini/Pictures/Screenshots/Captura de pantalla 2025-06-16 111833.png", width=200)

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
        
    

    if st.button("🔙 Volver"):
        # Limpiar estados temporales al volver
            st.session_state.tipo_usuario = None
            st.session_state.pantalla = None
            st.session_state.tipo_usuario = None
            st.session_state.pantalla = None
            st.session_state.pantalla = "login"
            st.rerun()

# Pantalla de login
elif st.session_state.pantalla == "login":
    st.subheader("🔐 Iniciar Sesión")
    
    # Seleccionar tipo de usuario
    tipo_login = st.selectbox("👤 Soy un:", ["Paciente", "Médico"])
    
    # Campos de login
    email_login = st.text_input("📧 Email")
    contraseña_login = st.text_input("🔑 Contraseña", type="password")
    
    # Botones en columnas
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Iniciar Sesión", use_container_width=True):
            if email_login and contraseña_login:
                # Convertir tipo a formato interno
                tipo_usuario_login = "paciente" if tipo_login == "Paciente" else "medico"
                
                # Intentar autenticar
                resultado = autenticar_usuario_con_verificacion(email_login, contraseña_login, tipo_usuario_login)
                
                if resultado['success']:
                    # Login exitoso
                    st.session_state.usuario_autenticado = resultado['usuario']
                    st.session_state.tipo_usuario = resultado['tipo']
                    st.session_state.nombre_usuario = f"{resultado['usuario']['nombre']} {resultado['usuario']['apellido']}"
                    st.session_state.pantalla = "perfil"
                    st.success(f"¡Bienvenido, {st.session_state.nombre_usuario}!")
                    st.rerun()
                else:
                    # Mostrar mensaje de error único
                    st.error(f"❌ {resultado['error']}")
            else:
                st.warning("⚠️ Por favor, completa todos los campos.")
    
    with col2:
        if st.button("🔙 Volver", use_container_width=True):
            st.session_state.pantalla = None
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
        

            # Opcional: Mostrar hospitales existentes como ayuda
        with st.expander("📋 Seleccionar Hospital Existente", expanded=False):
            hospitales_existentes = obtener_hospitales_existentes()
            if hospitales_existentes:
                st.info("**Hospitales ya registrados:**")
                for i, hosp in enumerate(hospitales_existentes):
                    direccion = formatear_direccion(hosp.get('provincia', ''), hosp.get('ciudad', ''), hosp.get('calle', ''), hosp.get('altura', ''))
                    if st.button(
                        f"• **{hosp['desc_hospital']}** - {direccion} ", 
                        key=f"hospital_{i}_{hosp['id_hospital']}"
                    ):
                        # Seleccionar este hospital
                        st.session_state.hospital_seleccionado = hosp
                        st.session_state.hospital_verificado = True
                        st.session_state.hospital_existe = True
                        st.session_state.mostrar_campos_hospital = False
                        st.session_state.datos_hospital_temp = {
                            'nombre': hosp['desc_hospital'],
                            'datos_existente': hosp
                        }
                        st.rerun()
                

            else:
                st.info("No hay hospitales registrados aún.")
            


        # Campo para el nombre del hospital
        col1, col2 = st.columns([3, 1])
        with col1:
            hospital = st.text_input("¿No encuentra el Hospital donde trabaja? ¡Regístrelo!", 
                                   value=st.session_state.datos_hospital_temp.get('nombre', ''))
        
        
            if st.button("🔍 Verificar", disabled=not hospital):
                if hospital:
                    # Buscar el hospital en la base de datos
                    hospital_encontrado = buscar_hospital_por_nombre(hospital)
                    
                    if hospital_encontrado:
                        direccion = formatear_direccion(hospital_encontrado.get('provincia', ''), hospital_encontrado.get('ciudad', ''), hospital_encontrado.get('calle', ''), hospital_encontrado.get('altura', ''))
                        st.success(f"✅ Hospital encontrado: {hospital_encontrado['desc_hospital']}")
                        st.info(f"📍 {direccion}")
                        st.info(f"📞 {hospital_encontrado.get('telefono', 'N/A')}")

                    else:
                        st.session_state.hospital_existe = False
                        st.session_state.hospital_verificado = True
                        st.session_state.mostrar_campos_hospital = True
                        st.session_state.datos_hospital_temp['nombre'] = hospital
                        st.warning("⚠️ Hospital no encontrado. Por favor, ingresa los datos del hospital.")
                        st.rerun()
        

        
        # Campos adicionales si el hospital no existe
        provincia_hospital = None
        ciudad_hospital = None
        calle_hospital = None
        altura_hospital = None
        telefono_hospital = None
        
        if st.session_state.mostrar_campos_hospital:
            st.markdown("### Datos del Nuevo Hospital")
            provincia_hospital = st.text_input("🌎 Provincia", value=st.session_state.datos_hospital_temp.get('provincia', ''))
            ciudad_hospital = st.text_input("🏙️ Ciudad", value=st.session_state.datos_hospital_temp.get('ciudad', ''))
            calle_hospital = st.text_input("🚏 Calle", value=st.session_state.datos_hospital_temp.get('calle', ''))
            altura_hospital = st.text_input("🔢 Altura", value=st.session_state.datos_hospital_temp.get('altura', ''))
            telefono_hospital = st.text_input("📞 Teléfono del Hospital", value=st.session_state.datos_hospital_temp.get('telefono', ''))
            
            # Guardar datos temporalmente
            st.session_state.datos_hospital_temp.update({
                'provincia': provincia_hospital,
                'ciudad': ciudad_hospital,
                'calle': calle_hospital,
                'altura': altura_hospital,
                'telefono': telefono_hospital
            })
        
     
    elif tipo == "paciente":
        fecha_de_nacimiento = st.date_input("📅 Fecha de nacimiento",
    min_value=min_date,  # Establecer el límite inferior
    max_value=max_date,  # Establecer el límite superior
    value=date.today()  # Establece la fecha predeterminada (la fecha de hoy)
    )
        provincia = st.text_input("🌎 Provincia")
        ciudad = st.text_input("🏙️ Ciudad")
        calle = st.text_input("🚏 Calle")
        altura = st.text_input("🔢 Altura")
        obra_social = st.selectbox("🏥 Obra social", OBRAS_SOCIALES, index=0)
        correo = st.text_input("�� Correo electrónico")
        contraseña = st.text_input("🔑 Contraseña", type="password")
    
    # Botón de registro
    if st.button("✅ Registrarme"):
        tipo = st.session_state.tipo_usuario
        
        # Verificar si el email ya está registrado como otro tipo
        if correo:
            verificacion_email = verificar_usuario_existente(correo)
            if verificacion_email['success'] and verificacion_email['existe']:
                tipo_existente = verificacion_email['tipo_existente']
                if tipo_existente == 'ambos':
                    st.error(f"❌ {verificacion_email['mensaje']}")
                    st.stop()
                elif tipo_existente != tipo:
                    st.error(f"❌ {verificacion_email['mensaje']} Si quieres registrarte como {'paciente' if tipo == 'medico' else 'médico'}, por favor selecciona el tipo correcto.")
                    st.stop()
        
        if tipo == "paciente":
            # Lógica para paciente (sin cambios)
            if dni and apellido and nombre and fecha_de_nacimiento and sexo and provincia and ciudad and calle and altura and obra_social and correo and contraseña:
                resultado = registrar_usuario(
                    dni=dni,
                    apellido=apellido,
                    nombre=nombre,
                    fecha_de_nacimiento=fecha_de_nacimiento,
                    sexo=sexo,
                    provincia=provincia,
                    ciudad=ciudad,
                    calle=calle,
                    altura=altura,
                    obra_social=obra_social,
                    correo=correo,
                    contraseña=contraseña
                )
                if resultado['success']:
                    st.success("✅ Paciente registrado con éxito.")
                else:
                    st.error(f"❌ Error al registrar el paciente: {resultado.get('error', 'Error desconocido')}")
            else:
                st.warning("⚠️ Completá todos los campos antes de continuar.")
                
        elif tipo == "medico":
            # Validación completa para médico
            campos_basicos_completos = dni and apellido and nombre and sexo and telefono and correo and contraseña and hospital
            hospital_verificado_ok = st.session_state.hospital_verificado
            
            # Si el hospital no existe, validar que se hayan ingresado los datos adicionales
            datos_hospital_completos = True
            if st.session_state.mostrar_campos_hospital:
                datos_hospital_completos = provincia_hospital and ciudad_hospital and calle_hospital and altura_hospital and telefono_hospital
            
            if campos_basicos_completos and hospital_verificado_ok and datos_hospital_completos:
                # Proceder con el registro
                resultado = registrar_medico_con_hospital(
                    dni=dni,
                    apellido=apellido,
                    nombre=nombre,
                    sexo=sexo,
                    nombre_hospital=hospital,
                    provincia_hospital= provincia_hospital,
                    ciudad_hospital= ciudad_hospital,
                    calle_hospital= calle_hospital,
                    altura_hospital= altura_hospital,
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
                    if not provincia_hospital: st.write("- Provincia del hospital")
                    if not ciudad_hospital: st.write("- Ciudad del hospital")
                    if not calle_hospital: st.write("- Calle del hospital")
                    if not altura_hospital: st.write("- Altua del hospital")
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

# Pantalla de perfil (después del login exitoso)
elif st.session_state.pantalla == "perfil":
    if "usuario_autenticado" not in st.session_state:
        st.error("❌ No hay usuario autenticado")
        st.session_state.pantalla = None
        st.rerun()
    
    usuario = st.session_state.usuario_autenticado
    tipo = st.session_state.tipo_usuario
    
    # Header con información del usuario
    st.markdown(f"""
    <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1976d2; margin: 0;'>👋 ¡Bienvenido, {st.session_state.nombre_usuario}!</h2>
        <p style='color: #424242; margin: 5px 0;'>Tipo de usuario: {'Médico' if tipo == 'medico' else 'Paciente'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información del perfil
    st.subheader("📋 Información del Perfil")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**🆔 DNI:** {usuario.get('id_paciente' if tipo == 'paciente' else 'id_medico', 'N/A')}")
        st.write(f"**👤 Nombre:** {usuario.get('nombre', 'N/A')}")
        st.write(f"**👤 Apellido:** {usuario.get('apellido', 'N/A')}")
        st.write(f"**⚧ Sexo:** {usuario.get('sexo', 'N/A')}")
        
        if tipo == "paciente":
            st.write(f"**📅 Fecha de nacimiento:** {usuario.get('fecha_de_nacimiento', 'N/A')}")
            direccion = formatear_direccion(usuario.get('provincia', ''), usuario.get('ciudad', ''), usuario.get('calle', ''), usuario.get('altura', ''))
            st.write(f"**Dirección:** {direccion}")
            st.write(f"**🏥 Obra social:** {usuario.get('obra_social', 'N/A')}")
        else:  # médico
            st.write(f"**📞 Teléfono:** {usuario.get('telefono', 'N/A')}")
            st.write(f"**🏥 Hospital:** {usuario.get('desc_hospital', 'N/A')}")
    
    with col2:
        st.write(f"**📧 Email:** {usuario.get('email', 'N/A')}")
        # Botones de acción
        st.markdown("---")
        st.subheader("🔧 Acciones")
        if st.button("📝 Editar Perfil", use_container_width=True):
            st.session_state.pantalla = "editar_perfil"
            st.rerun()
        st.markdown("---")
        # Botón de logout
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="primary"):
            # Limpiar datos de sesión
            st.session_state.usuario_autenticado = None
            st.session_state.tipo_usuario = None
            st.session_state.nombre_usuario = "Usuario"
            st.session_state.pantalla = None
            st.success("✅ Sesión cerrada exitosamente")
            st.rerun()

    # Mostrar menú de navegación (fuera del with col2:)
    mostrar_menu_navegacion()

# Pantalla de editar perfil
elif st.session_state.pantalla == "editar_perfil":
    if "usuario_autenticado" not in st.session_state:
        st.error("❌ No hay usuario autenticado")
        st.session_state.pantalla = None
        st.rerun()
    
    usuario = st.session_state.usuario_autenticado
    tipo = st.session_state.tipo_usuario
    
    st.title("📝 Editar Perfil")
    st.markdown("---")
    
    # Formulario de edición
    with st.form("editar_perfil_form"):
        st.subheader("📋 Información Personal")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dni = st.text_input("🆔 DNI", value=usuario.get('id_paciente' if tipo == 'paciente' else 'id_medico', ''), disabled=True)
            nombre = st.text_input("👤 Nombre", value=usuario.get('nombre', ''))
            apellido = st.text_input("👤 Apellido", value=usuario.get('apellido', ''))
            sexo = st.selectbox("⚧ Sexo", ["M", "F", "O"], index=["M", "F", "O"].index(usuario.get('sexo', 'M')))
        
        with col2:
            if tipo == "paciente":
                fecha_de_nacimiento = st.date_input("📅 Fecha de nacimiento", value=usuario.get('fecha_de_nacimiento'))
            else:
                telefono = st.text_input("📞 Teléfono", value=usuario.get('telefono', ''))
        
        st.markdown("---")
        
        if tipo == "paciente":
            st.subheader("🏠 Información de Contacto")
            col1, col2 = st.columns(2)
            
            with col1:
                provincia = st.text_input("🌎 Provincia", value=usuario.get('provincia', ''))
                ciudad = st.text_input("🏙️ Ciudad", value=usuario.get('ciudad', ''))
                calle = st.text_input("🚏 Calle", value=usuario.get('calle', ''))
                altura = st.text_input("🔢 Altura", value=usuario.get('altura', ''))
            
            with col2:
                obra_social = st.selectbox("🏥 Obra social", OBRAS_SOCIALES, index=OBRAS_SOCIALES.index(usuario.get('obra_social')) if usuario.get('obra_social') in OBRAS_SOCIALES else 0)
        else:
            st.subheader("🏥 Información del Hospital")
            hospital_info = obtener_hospital_por_id(usuario.get('id_hospital'))
            if hospital_info:
                direccion = formatear_direccion(hospital_info.get('provincia', ''), hospital_info.get('ciudad', ''), hospital_info.get('calle', ''), hospital_info.get('altura', ''))
                st.info(f"🏥 **Hospital:** {hospital_info.get('desc_hospital', 'N/A')}")
                st.info(f"📍 **Dirección:** {direccion}")
                st.info(f"📞 **Teléfono:** {hospital_info.get('telefono', 'N/A')}")
            else:
                st.warning("⚠️ No se pudo obtener la información del hospital")
        
        st.markdown("---")
        
        st.subheader("📧 Información de Acceso")
        col1, col2 = st.columns(2)
        
        with col1:
            correo = st.text_input("📧 Correo electrónico", value=usuario.get('email', ''))
        
        with col2:
            contraseña = st.text_input("🔑 Nueva contraseña (dejar vacío para mantener la actual)", type="password")
        
        st.markdown("---")
        
        # Botones del formulario
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                # Validar campos obligatorios
                campos_obligatorios = [nombre, apellido, correo]
                if tipo == "paciente":
                    campos_obligatorios.extend([provincia, ciudad, calle, obra_social])
                else:
                    campos_obligatorios.append(telefono)
                
                if all(campos_obligatorios):
                    # Usar contraseña actual si no se proporciona una nueva
                    contraseña_final = contraseña if contraseña else usuario.get('contraseña', '')
                    
                    if tipo == "paciente":
                        resultado = actualizar_paciente(
                            dni=dni,
                            apellido=apellido,
                            nombre=nombre,
                            fecha_de_nacimiento=fecha_de_nacimiento,
                            sexo=sexo,
                            provincia=provincia,
                            ciudad=ciudad,
                            calle=calle,
                            altura=altura,
                            obra_social=obra_social,
                            correo=correo,
                            contraseña=contraseña_final
                        )
                    else:
                        resultado = actualizar_medico(
                            dni=dni,
                            apellido=apellido,
                            nombre=nombre,
                            sexo=sexo,
                            id_hospital=usuario.get('id_hospital'),
                            telefono=telefono,
                            correo=correo,
                            contraseña=contraseña_final
                        )
                    
                    if resultado['success']:
                        # Actualizar datos en session_state
                        st.session_state.usuario_autenticado = resultado['usuario']
                        st.session_state.nombre_usuario = f"{resultado['usuario']['nombre']} {resultado['usuario']['apellido']}"
                        st.success("✅ Perfil actualizado exitosamente")
                        st.session_state.pantalla = "perfil"
                        st.rerun()
                    else:
                        st.error(f"❌ Error al actualizar perfil: {resultado['error']}")
                else:
                    st.error("❌ Por favor, completa todos los campos obligatorios")
        
        
        with col2:
            if st.form_submit_button("🔙 Cancelar", use_container_width=True):
                st.session_state.pantalla = "perfil"
                st.rerun()

def solo_medico_autenticado():
    """
    Permite el acceso solo si el usuario está autenticado y es médico.
    Si no, muestra un mensaje y detiene la ejecución de la página.
    """
    if "usuario_autenticado" not in st.session_state or st.session_state.usuario_autenticado is None:
        st.error("🔐 Debes iniciar sesión como médico para acceder a esta página")
        if st.button("🏠 Ir a la página principal"):
            st.switch_page("Inicio.py")
        st.stop()
    if st.session_state.get("tipo_usuario") != "medico":
        st.error("❌ Solo los médicos pueden acceder a esta página.")
        if st.button("🔙 Volver al perfil"):
            st.switch_page("Inicio.py")
        st.stop()

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

