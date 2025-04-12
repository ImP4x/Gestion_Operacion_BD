import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from pymongo import MongoClient
from bson.decimal128 import Decimal128
from io import BytesIO

app = Flask(__name__)
app.static_folder = 'static'

# Conexión a MongoDB Atlas
client = MongoClient(os.environ.get("DATABASE_URL","mongodb+srv://p4x:OAfFa78Cr1xmAoGJ@cluster0.flejnc5.mongodb.net/"))
db = client.avicola
huevos_col = db.huevos

PRECIOS = {
    "ROJO": {"A": 12000.0, "AA": 13500.0, "B": 11000.0, "EXTRA": 15000.0},
    "BLANCO": {"A": 10000.0, "AA": 11500.0, "B": 9500.0, "EXTRA": 14000.0}
}

# Filtro personalizado para formato de moneda
@app.template_filter('number_format')
def number_format(value):
    if value is None:
        return "N/A"
    if isinstance(value, Decimal128):
        value = float(value.to_decimal())
    try:
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"${formatted}"
    except:
        return "N/A"

# Inicializar precios en MongoDB
with app.app_context():
    for tipo, tamanios in PRECIOS.items():
        for tamanio, precio in tamanios.items():
            huevos_col.update_one(
                {"tipo": tipo, "tamanio": tamanio},
                {"$setOnInsert": {"precio": precio, "stock": 0}},
                upsert=True
            )

@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route('/Home')
def home():
    return render_template('home.html')

@app.route('/Insertar', methods=['GET', 'POST'])
def insertar():
    if request.method == 'POST':
        tipo = request.form['tipo']
        tamanio = request.form['tamanio']
        cubetas = int(request.form['cubetas'])
        huevos = cubetas * 30  # Convertir cubetas a huevos

        # Actualizar stock
        huevos_col.update_one(
            {"tipo": tipo, "tamanio": tamanio},
            {"$inc": {"stock": huevos}},
            upsert=True
        )
        return redirect(url_for('registros'))
    
    return render_template('insertar.html')

@app.route('/Comprar', methods=['GET', 'POST'])
def comprar():
    if request.method == 'POST':
        tipo_cliente = request.form['tipo_cliente']
        tipo_huevo = request.form['tipo_huevo']
        tamanio = request.form['tamanio']
        cantidad = int(request.form['cantidad'])
        nombre_cliente = request.form['nombre_cliente']
        documento = request.form['documento']
        
        # Calcular unidades necesarias
        if tipo_cliente == "natural":
            unidad = request.form['unidad']
            if unidad == "docenas":
                huevos_necesarios = cantidad * 12
            else:
                huevos_necesarios = cantidad * 30
        else:
            unidad = "cubetas"
            huevos_necesarios = cantidad * 30

        # Validar stock
        huevo = huevos_col.find_one({"tipo": tipo_huevo, "tamanio": tamanio})
        if not huevo or huevo['stock'] < huevos_necesarios:
            return render_template('comprar.html', error="Stock insuficiente")

        # Actualizar stock
        huevos_col.update_one(
            {"_id": huevo['_id']},
            {"$inc": {"stock": -huevos_necesarios}}
        )

        # Generar factura
        return generar_factura(
            nombre_cliente=nombre_cliente,
            documento=documento,
            tipo=tipo_huevo,
            tamanio=tamanio,
            cantidad=cantidad,
            unidad=unidad,
            tipo_cliente=tipo_cliente
        )
    
    return render_template('comprar.html')

def generar_factura(**kwargs):
    logo = r"""
       .==;=.                            
      / _  _ \                           
     |  o  o  |                          
     \   /\   /             ,            
    ,/'-=\/=-'\,    |\   /\/ \/|   ,_    
   / /        \ \   ; \\/`     '; , \_',  
  | /          \ |   \        /          
  \/ \        / \/    '.    .'    /`.    
      '.    .'          `~~` , /\ ``     
      _|`~~`|_              .  `         
      /|\  /|\                           
    """

    # Cálculo corregido para docenas
    precio_cubeta = PRECIOS[kwargs['tipo']][kwargs['tamanio']]
    
    if kwargs['unidad'] == 'docenas':
        precio_unitario = (precio_cubeta / 30) * 12  # Precio por docena
    else:
        precio_unitario = precio_cubeta  # Precio por cubeta

    subtotal = precio_unitario * kwargs['cantidad']
    iva = subtotal * 0.05
    total = subtotal + iva

    factura_content = f"""
{logo}
Avícola Llano Grande SAS
NIT: 870545489-0
--------------------------
FACTURA DE VENTA
Cliente: {kwargs['nombre_cliente']}
Documento: {kwargs['documento']}
Producto: {kwargs['tipo']} {kwargs['tamanio']}
Cantidad: {kwargs['cantidad']} {kwargs['unidad']}
Precio unitario: ${precio_unitario:,.2f}
Subtotal: ${subtotal:,.2f}
IVA (5%): ${iva:,.2f}
Total: ${total:,.2f}
    """

    return send_file(
        BytesIO(factura_content.encode('utf-8')),
        as_attachment=True,
        download_name='factura.txt',
        mimetype='text/plain'
    )

@app.route('/Registros')
def registros():
    inventario = list(huevos_col.find())
    return render_template('registros.html', inventario=inventario)

# Configuración para Vercel
if __name__ == "__vgi__":
    import serverless_wsgi
    handler = serverless_wsgi.handle_request(app)

if __name__ == '__main__':
    app.run(debug=True)