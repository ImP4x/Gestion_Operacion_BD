# Implementar librerias de MySQL y Postgrest
import pymysql
import psycopg2

# Configuración de conexiones
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "database": "sakila"
}

POSTGRES_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "admin",
    "database": "prueba"
}

# Función para conectar a MySQL
def connect_mysql():
    return pymysql.connect(**MYSQL_CONFIG)

# Función para conectar a PostgreSQL
def connect_postgres():
    return psycopg2.connect(**POSTGRES_CONFIG)

# Función para obtener un FULL JOIN simulado de ambas bases de datos
def full_join_tables():
    mysql_conn = connect_mysql()
    postgres_conn = connect_postgres()

    try:
        mysql_cursor = mysql_conn.cursor()
        postgres_cursor = postgres_conn.cursor()

        # Obtener datos de MySQL (tabla 'actor')
        mysql_cursor.execute("SELECT actor_id, first_name, last_name FROM actor;")
        mysql_data = mysql_cursor.fetchall()

        # Obtener datos de PostgreSQL (tabla 'employees')
        postgres_cursor.execute("SELECT employee_id, first_name, last_name FROM employees;")
        postgres_data = postgres_cursor.fetchall()

        # Convertir datos a diccionario para simular un FULL JOIN
        data_dict = {}

        # Agregar datos de MySQL
        for row in mysql_data:
            data_dict[f"mysql_{row[0]}"] = {
                "id": row[0], 
                "first_name": row[1], 
                "last_name": row[2], 
                "source": "MySQL"
            }

        # Agregar datos de PostgreSQL
        for row in postgres_data:
            key = f"postgres_{row[0]}"
            if key in data_dict:
                data_dict[key]["source"] += " & PostgreSQL"
            else:
                data_dict[key] = {
                    "id": row[0], 
                    "first_name": row[1], 
                    "last_name": row[2], 
                    "source": "PostgreSQL"
                }

        # Imprimir los datos en formato de tabla
        print("\n--- FULL JOIN de MySQL y PostgreSQL ---")
        print(f"{'ID':<5} {'Nombre':<15} {'Apellido':<15} {'Fuente':<20}")
        print("-" * 55)
        for key, value in sorted(data_dict.items(), key=lambda x: x[1]['id']):
            print(f"{value['id']:<5} {value['first_name']:<15} {value['last_name']:<15} {value['source']:<20}")

    finally:
        mysql_cursor.close()
        mysql_conn.close()
        postgres_cursor.close()
        postgres_conn.close()

# CRUD - Actualizar registros en ambas bases de datos
def actualizar_registro():
    id_usuario = input("Ingrese el ID del usuario a actualizar: ")
    nuevo_nombre = input("Ingrese el nuevo nombre: ")
    nuevo_apellido = input("Ingrese el nuevo apellido: ")

    mysql_conn = connect_mysql()
    postgres_conn = connect_postgres()

    try:
        mysql_cursor = mysql_conn.cursor()
        postgres_cursor = postgres_conn.cursor()

        # Actualizar en MySQL (tabla 'actor')
        mysql_cursor.execute(
            "UPDATE actor SET first_name=%s, last_name=%s WHERE actor_id=%s;", 
            (nuevo_nombre, nuevo_apellido, id_usuario)
        )
        mysql_conn.commit()

        # Actualizar en PostgreSQL (tabla 'employees')
        postgres_cursor.execute(
            "UPDATE employees SET first_name=%s, last_name=%s WHERE employee_id=%s;", 
            (nuevo_nombre, nuevo_apellido, id_usuario)
        )
        postgres_conn.commit()

        print("Registro actualizado en ambas bases de datos.")

    finally:
        mysql_cursor.close()
        mysql_conn.close()
        postgres_cursor.close()
        postgres_conn.close()

# Menú principal
def menu():
    while True:
        print("\n--- MENÚ ---")
        print("1. Mostrar FULL JOIN de ambas bases de datos")
        print("2. Actualizar un usuario en ambas bases de datos")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            full_join_tables()
        elif opcion == "2":
            actualizar_registro()
        elif opcion == "3":
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida, intente nuevamente.")

# Ejecutar el menú
if __name__ == "__main__":
    menu()