# Importar las bibliotecas necesarias
import os  # Para interactuar con variables de entorno (no se usa directamente aquí, pero es útil en otros casos)
import psycopg2  # Biblioteca para conectarse a PostgreSQL (CockroachDB es compatible con PostgreSQL)
from psycopg2 import sql  # Para construir consultas SQL de manera segura (no se usa aquí, pero es útil en otros casos)

# Configura la cadena de conexión a la base de datos CockroachDB
DATABASE_URL = "postgresql://willian:vCWiu5GSzLMBmlkUNdPskw@fanged-oyster-4710.jxf.gcp-us-east1.cockroachlabs.cloud:26257/prueba?sslmode=verify-full"

# Función para conectar a la base de datos
def conectar_db():
    """
    Conecta a la base de datos usando la cadena de conexión DATABASE_URL.
    Retorna la conexión si es exitosa, o None si falla.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)  # Intenta conectarse a la base de datos
        return conn  # Retorna la conexión
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")  # Si hay un error, lo muestra
        return None  # Retorna None si la conexión falla

# Función para mostrar todos los datos de la tabla personas
def mostrar_datos(conn):
    """
    Muestra todos los registros de la tabla 'personas'.
    """
    try:
        with conn.cursor() as cur:  # Abre un cursor para ejecutar consultas
            cur.execute("SELECT * FROM personas")  # Ejecuta una consulta para obtener todos los datos
            rows = cur.fetchall()  # Recupera todos los resultados de la consulta
            if rows:  # Si hay datos, los muestra
                print("\nDatos en la tabla personas:")
                for row in rows:  # Itera sobre cada fila de resultados
                    print(f"ID: {row[0]}, Nombre: {row[1]}, Apellido: {row[2]}, Edad: {row[3]}")
            else:  # Si no hay datos, muestra un mensaje
                print("\nNo hay datos en la tabla personas.")
    except Exception as e:
        print(f"Error al mostrar datos: {e}")  # Si hay un error, lo muestra

# Función para insertar datos en la tabla personas
def insertar_datos(conn):
    """
    Solicita al usuario los datos de una nueva persona y los inserta en la tabla 'personas'.
    """
    try:
        # Solicita los datos al usuario
        nombre = input("Ingrese el nombre: ")
        apellido = input("Ingrese el apellido: ")
        edad = int(input("Ingrese la edad: "))

        with conn.cursor() as cur:  # Abre un cursor para ejecutar consultas
            # Ejecuta una consulta para insertar los datos
            cur.execute(
                "INSERT INTO personas (nombre, apellido, edad) VALUES (%s, %s, %s)",
                (nombre, apellido, edad)
            )
            conn.commit()  # Confirma la transacción
            print("\nDatos insertados correctamente.")  # Muestra un mensaje de éxito
    except Exception as e:
        print(f"Error al insertar datos: {e}")  # Si hay un error, lo muestra

# Función para eliminar datos de la tabla personas
def eliminar_datos(conn):
    """
    Solicita al usuario el ID de una persona y elimina su registro de la tabla 'personas'.
    """
    try:
        # Solicita el ID de la persona a eliminar
        id_persona = input("Ingrese el ID de la persona a eliminar: ")

        with conn.cursor() as cur:  # Abre un cursor para ejecutar consultas
            # Ejecuta una consulta para eliminar el registro
            cur.execute("DELETE FROM personas WHERE id = %s", (id_persona,))
            conn.commit()  # Confirma la transacción
            print("\nDatos eliminados correctamente.")  # Muestra un mensaje de éxito
    except Exception as e:
        print(f"Error al eliminar datos: {e}")  # Si hay un error, lo muestra

# Función para mostrar el menú y manejar las opciones
def menu():
    """
    Muestra un menú de opciones y ejecuta la función correspondiente según la elección del usuario.
    """
    conn = conectar_db()  # Conecta a la base de datos
    if not conn:  # Si la conexión falla, termina el programa
        return

    while True:  # Bucle infinito para mostrar el menú hasta que el usuario elija salir
        print("\n--- Menú CRUD ---")
        print("1. Mostrar datos")
        print("2. Insertar datos")
        print("3. Eliminar datos")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")  # Solicita la opción al usuario

        if opcion == "1":  # Si elige 1, muestra los datos
            mostrar_datos(conn)
        elif opcion == "2":  # Si elige 2, inserta datos
            insertar_datos(conn)
        elif opcion == "3":  # Si elige 3, elimina datos
            eliminar_datos(conn)
        elif opcion == "4":  # Si elige 4, sale del programa
            print("Saliendo del programa...")
            break
        else:  # Si la opción no es válida, muestra un mensaje
            print("Opción no válida. Intente de nuevo.")

    conn.close()  # Cierra la conexión a la base de datos al salir del programa

# Punto de entrada del programa
if __name__ == "__main__":
    menu()  # Ejecuta la función del menú