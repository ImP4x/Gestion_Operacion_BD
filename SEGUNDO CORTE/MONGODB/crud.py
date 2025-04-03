import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import matplotlib.pyplot as plt
import pandas as pd

# Conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['basesprueba']
collection = db['ba']

# Funciones CRUD modificadas
def create_document():
    print("\n--- Crear nuevo documento ---")
    nuevo_doc = {
        "Nombre_Tipo": input("Tipo de Caso: "),
        "Total_Victimas_Caso": int(input("Total de Victimas: ")),
        "Nombre_Departamento": input("Departamento: "),
        "Nombre_Nunicipio": input("Municipio: "),
        "Anio_hecho": int(input("Año del hecho: ")),
        "mes_hecho": int(input("Mes del hecho (1-12): ")),
        "dia_hecho": int(input("Dia del hecho: ")),
        "Presunto_Responsable": input("Presunto Responsable: "),
        "Modalidad": input("Modalidad: ")
    }
    result = collection.insert_one(nuevo_doc)
    print(f"\nDocumento creado con ID: {result.inserted_id}")

def read_documents():
    print("\n--- Últimos 10 documentos ---")
    documents = collection.find().sort('_id', -1).limit(10)
    for doc in documents:
        print(f"""
        ID: {doc['_id']}
        Tipo de Caso: {doc.get('Nombre_Tipo', 'N/A')}
        Total de Victimas: {doc.get('Total_Victimas_Caso', 'N/A')}
        Departamento: {doc.get('Nombre_Departamento', 'N/A')}
        Municipio: {doc.get('Nombre_Nunicipio', 'N/A')}
        Año del hecho: {doc.get('Anio_hecho', 'N/A')}
        Mes del hecho: {doc.get('mes_hecho', 'N/A')}
        Dia del hecho: {doc.get('dia_hecho', 'N/A')}
        Presunto Responsable: {doc.get('Presunto_Responsable', 'N/A')}
        Modalidad: {doc.get('Modalidad', 'N/A')}
        """)

def update_document():
    print("\n--- Actualizar documento ---")
    doc_id = input("Ingrese el ID del documento a actualizar: ")
    try:
        updates = {
            "Nombre_Tipo": input("Nuevo | Tipo de Caso: "),
            "Total_Victimas_Caso": int(input("Nuevo | Total de Victimas: ")),
            "Nombre_Departamento": input("Nuevo | Departamento: "),
            "Nombre_Nunicipio": input("Nuevo | Municipio: "),
            "Anio_hecho": int(input("Nuevo | Año del hecho: ")),
            "mes_hecho": int(input("Nuevo | Mes del hecho (1-12): ")),
            "dia_hecho": int(input("Nuevo | Dia del hecho: ")),
            "Presunto_Responsable": input("Nuevo Presunto | Responsable: "),
            "Modalidad": input("Nueva | Modalidad: ")
        }
        result = collection.update_one(
            {'_id': ObjectId(doc_id)},
            {'$set': updates}
        )
        print(f"\nDocumentos actualizados: {result.modified_count}")
    except Exception as e:
        print(f"Error: {str(e)}")

def delete_document():
    print("\n--- Eliminar documento ---")
    doc_id = input("Ingrese el ID del documento a eliminar: ")
    try:
        result = collection.delete_one({'_id': ObjectId(doc_id)})
        print(f"\nDocumentos eliminados: {result.deleted_count}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Generar y exportar gráfica en PDF
def generate_plot():
    documents = collection.find().limit(10)
    df = pd.DataFrame(list(documents))
    
    if not df.empty:
        plt.figure(figsize=(15, 6))
        
        # Gráfico de víctimas por mes
        plt.subplot(131)
        df['mes_hecho'] = df['mes_hecho'].astype(int)
        month_counts = df['mes_hecho'].value_counts().sort_index()
        month_counts.plot(kind='bar', color='#1f77b4')
        plt.title('Casos por mes')
        plt.xlabel('Mes')
        plt.ylabel('Cantidad de casos')
        
        # Gráfico de responsables
        plt.subplot(132)
        responsible_counts = df['Presunto_Responsable'].value_counts()
        responsible_counts.plot(kind='bar', color='#2ca02c')
        plt.title('Distribución de responsables')
        plt.xticks(rotation=45)
        
        # Gráfico de modalidades
        plt.subplot(133)
        modalidad_counts = df['Modalidad'].value_counts()
        modalidad_counts.plot(kind='barh', color='#ff7f0e')
        plt.title('Tipos de modalidad')
        
        plt.tight_layout()
        plt.savefig('casos.pdf', format='pdf')
        print("\nGráfica exportada como 'casos.pdf'")
    else:
        print("No hay datos para graficar")

# Menú interactivo
def main_menu():
    while True:
        print("\n==== MENÚ PRINCIPAL ====")
        print("1. Crear nuevo documento")
        print("2. Leer últimos documentos")
        print("3. Actualizar documento")
        print("4. Eliminar documento")
        print("5. Generar gráfica")
        print("6. Salir")
        
        choice = input("\nSeleccione una opción: ")
        
        if choice == '1':
            create_document()
        elif choice == '2':
            read_documents()
        elif choice == '3':
            update_document()
        elif choice == '4':
            delete_document()
        elif choice == '5':
            generate_plot()
        elif choice == '6':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main_menu()