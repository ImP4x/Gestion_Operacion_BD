import pandas as pd
from sqlalchemy import create_engine

# Configuración de la conexión a la base de datos MySQL
# Reemplaza con tus credenciales y detalles de la base de datos
usuario = "root"  # Usuario de MySQL
contraseña = ""  # Contraseña de MySQL
host = "localhost"  # Host de la base de datos
puerto = "3306"  # Puerto de MySQL (por defecto es 3306)
nombre_base_de_datos = "sakila"  # Nombre de la base de datos

# Crear la cadena de conexión para MySQL
cadena_conexion = f"mysql+pymysql://{usuario}:{contraseña}@{host}:{puerto}/{nombre_base_de_datos}"

# Crear el motor de SQLAlchemy
engine = create_engine(cadena_conexion)

# 1. INNER JOIN - Alquileres entre junio y julio de 2005
query_inner_join = """
SELECT 
    c.customer_id, 
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
    r.rental_id, 
    r.rental_date, 
    i.inventory_id, 
    f.film_id, 
    f.title, 
    fc.category_id
FROM customer c
INNER JOIN rental r ON c.customer_id = r.customer_id
INNER JOIN inventory i ON r.inventory_id = i.inventory_id
INNER JOIN film f ON i.film_id = f.film_id
INNER JOIN film_category fc ON f.film_id = fc.film_id
WHERE r.rental_date BETWEEN '2005-06-01' AND '2005-07-01';
"""

# Ejecutar la consulta y cargar los resultados en un DataFrame
df_inner_join = pd.read_sql(query_inner_join, engine)
print("Resultados del INNER JOIN:")
print(df_inner_join)

# 2. LEFT JOIN - Clientes activos, incluso si no han alquilado películas
query_left_join = """
SELECT 
    c.customer_id, 
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
    r.rental_id, 
    r.rental_date, 
    i.inventory_id
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
LEFT JOIN inventory i ON r.inventory_id = i.inventory_id
WHERE c.active = 1;
"""

# Ejecutar la consulta y cargar los resultados en un DataFrame
df_left_join = pd.read_sql(query_left_join, engine)
print("\nResultados del LEFT JOIN:")
print(df_left_join)

# 3. RIGHT JOIN - Películas con tarifa de alquiler mayor a 2.99
query_right_join = """
SELECT 
    s.staff_id, 
    CONCAT(s.first_name, ' ', s.last_name) AS staff_name, 
    i.inventory_id, 
    f.film_id, 
    f.title
FROM staff s
RIGHT JOIN inventory i ON s.store_id = i.store_id
RIGHT JOIN film f ON i.film_id = f.film_id
WHERE f.rental_rate > 2.99;
"""

# Ejecutar la consulta y cargar los resultados en un DataFrame
df_right_join = pd.read_sql(query_right_join, engine)
print("\nResultados del RIGHT JOIN:")
print(df_right_join)

# 4. FULL OUTER JOIN - Clientes sin alquileres, registros sin asignación de empleado o inventarios sin relación
# MySQL no soporta FULL OUTER JOIN directamente, por lo que se simula con UNION de LEFT y RIGHT JOIN
query_full_outer_join = """
SELECT 
    c.customer_id, 
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
    r.rental_id, 
    r.rental_date, 
    s.staff_id, 
    CONCAT(s.first_name, ' ', s.last_name) AS staff_name, 
    i.inventory_id
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
LEFT JOIN inventory i ON r.inventory_id = i.inventory_id
LEFT JOIN staff s ON r.staff_id = s.staff_id
WHERE r.rental_date IS NULL OR s.staff_id IS NULL OR i.inventory_id IS NULL
UNION
SELECT 
    c.customer_id, 
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
    r.rental_id, 
    r.rental_date, 
    s.staff_id, 
    CONCAT(s.first_name, ' ', s.last_name) AS staff_name, 
    i.inventory_id
FROM customer c
RIGHT JOIN rental r ON c.customer_id = r.customer_id
RIGHT JOIN inventory i ON r.inventory_id = i.inventory_id
RIGHT JOIN staff s ON r.staff_id = s.staff_id
WHERE r.rental_date IS NULL OR s.staff_id IS NULL OR i.inventory_id IS NULL;
"""

# Ejecutar la consulta y cargar los resultados en un DataFrame
df_full_outer_join = pd.read_sql(query_full_outer_join, engine)
print("\nResultados del FULL OUTER JOIN:")
print(df_full_outer_join)

# 5. CROSS JOIN - Combinaciones con los primeros 10 clientes
query_cross_join = """
SELECT 
    c.customer_id, 
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
    f.film_id, 
    f.title
FROM customer c
CROSS JOIN film f
WHERE c.customer_id < 10;
"""

# Ejecutar la consulta y cargar los resultados en un DataFrame
df_cross_join = pd.read_sql(query_cross_join, engine)
print("\nResultados del CROSS JOIN:")
print(df_cross_join)