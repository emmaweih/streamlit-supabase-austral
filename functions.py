import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

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
            print("Error: One or more Supabase environment variables are not set.")
            print("Please set SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME, SUPABASE_DB_USER, and SUPABASE_DB_PASSWORD.")
            return None

        # Establish the connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        print("Successfully connected to Supabase database.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to Supabase database: {e}")
        return None

connect_to_supabase()


def execute_query(query, params= None, conn=None, is_select=True):
    """
    Executes a SQL query and returns the results as a pandas DataFrame for SELECT queries,
    or executes DML operations (INSERT, UPDATE, DELETE) and returns success status.
    
    Args:
        query (str): The SQL query to execute
        conn (psycopg2.extensions.connection, optional): Database connection object.
            If None, a new connection will be established.
        is_select (bool, optional): Whether the query is a SELECT query (True) or 
            a DML operation like INSERT/UPDATE/DELETE (False). Default is True.
            
    Returns:
        pandas.DataFrame or bool: A DataFrame containing the query results for SELECT queries,
            or True for successful DML operations, False otherwise.
    """
    try:
        # Create a new connection if one wasn't provided
        close_conn = False
        if conn is None:
            conn = connect_to_supabase()
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
        print(f"Error executing query: {e}")
        # Rollback any changes if an error occurred during DML operation
        if conn and not is_select:
            conn.rollback()
        return pd.DataFrame() if is_select else False

def add_employee(nombre, dni, telefono, fecha_contratacion, salario):
    """
    Adds a new employee to the Empleado table.
    """

    query = "INSERT INTO empleado (nombre, dni, telefono, fecha_contratacion, salario) VALUES (%s, %s, %s, %s, %s)"
    params = (nombre, dni, telefono, fecha_contratacion, salario)
    
    return execute_query(query, params=params, is_select=False)


def registrar_usuario(dni, apellido, nombre, fecha_de_nacimiento, sexo, direccion, codigo_postal, obra_social, correo, contraseña):
    """
    Registra un nuevo usuario/paciente en la tabla paciente.
    
    Args:
        dni (str): DNI del paciente (usado como id_paciente)
        apellido (str): Apellido del paciente
        nombre (str): Nombre del paciente
        fecha_de_nacimiento (str/date): Fecha de nacimiento
        sexo (str): Sexo del paciente
        direccion (str): Dirección del paciente
        codigo_postal (str): Código postal
        obra_social (str): Obra social del paciente
        correo (str): Email del paciente
        contraseña (str): Contraseña del paciente
        
    Returns:
        bool: True si el registro fue exitoso, False en caso contrario
    """
    try:
        query = """
            INSERT INTO paciente (
                id_paciente, apellido, nombre, fecha_de_nacimiento,
                sexo, direccion, codigo_postal, obra_social,
                email, contraseña
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            dni, apellido, nombre, fecha_de_nacimiento,
            sexo, direccion, codigo_postal, obra_social,
            correo, contraseña
        )
        
        resultado = execute_query(query, params=params, is_select=False)
        
        if resultado:
            print(f"Usuario {nombre} {apellido} registrado exitosamente.")
            return True
        else:
            print(f"Error al registrar el usuario {nombre} {apellido}.")
            return False
            
    except Exception as e:
        print(f"Error en registrar_usuario: {e}")
        return False

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
        bool: True si el registro fue exitoso, False en caso contrario
    """
    try:
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
        
        resultado = execute_query(query, params=params, is_select=False)
        
        if resultado:
            print(f"Usuario {nombre} {apellido} registrado exitosamente.")
            return True
        else:
            print(f"Error al registrar el usuario {nombre} {apellido}.")
            return False
            
    except Exception as e:
        print(f"Error en registrar_usuario: {e}")
        return False
    
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

def agregar_nuevo_hospital(nombre, direccion, telefono):
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
                    INSERT INTO hospital (id_hospital, desc_hospital, direccion, telefono) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING *
                """, (next_id, nombre.strip(), direccion.strip(), telefono.strip()))
            else:
                # La tabla tiene secuencia, insertar normalmente
                cursor.execute("""
                    INSERT INTO hospital (desc_hospital, direccion, telefono) 
                    VALUES (%s, %s, %s) 
                    RETURNING *
                """, (nombre.strip(), direccion.strip(), telefono.strip()))
            
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

def obtener_o_crear_hospital(nombre, direccion=None, telefono=None):
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
        if not direccion or not telefono:
            return {
                'success': False,
                'error': 'Se requieren dirección y teléfono para crear un nuevo hospital'
            }
        
        resultado_nuevo = agregar_nuevo_hospital(nombre, direccion, telefono)
        
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
                                direccion_hospital=None, telefono_hospital=None,
                                telefono_medico=None, correo=None, contraseña=None):
    """
    Registra un médico y maneja la lógica del hospital (crear o usar existente)
    """
    try:
        # Paso 1: Obtener o crear el hospital
        resultado_hospital = obtener_o_crear_hospital(
            nombre=nombre_hospital,
            direccion=direccion_hospital,
            telefono=telefono_hospital
        )
        
        if not resultado_hospital['success']:
            return {
                'success': False,
                'mensaje': f"Error con el hospital: {resultado_hospital['error']}"
            }
        
        hospital = resultado_hospital['hospital']
        id_hospital = hospital['id_hospital']
        
        # Paso 2: Registrar el médico
        conn = get_db_connection()
        if not conn:
            return {
                'success': False,
                'mensaje': 'No se pudo conectar a la base de datos'
            }
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO medico (id_medico, apellido, nombre, sexo, id_hospital, telefono, email, contraseña) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                    RETURNING *
                """, (dni, apellido, nombre, sexo, id_hospital, telefono_medico, correo, contraseña))
                
                row = cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]
                medico = dict(zip(columns, row))
                
                conn.commit()
                
                return {
                    'success': True,
                    'medico': medico,
                    'datos_hospital': hospital,
                    'hospital_nuevo': resultado_hospital['es_nuevo']
                }
                
        except Exception as e:
            conn.rollback()
            print(f"Error al registrar médico: {e}")
            return {
                'success': False,
                'mensaje': f'Error al registrar el médico: {str(e)}'
            }
        finally:
            conn.close()
            
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