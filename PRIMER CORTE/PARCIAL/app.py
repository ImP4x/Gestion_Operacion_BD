import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, send_file
from io import BytesIO
from serverless_wsgi import handle_request
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.static_folder = 'static'

def get_db_connection():
    conn = psycopg2.connect(
        os.environ.get(
            "DATABASE_URL", "postgresql://willian:368g9xCJ22kfMgAt1aPgIA@fanged-oyster-4710.jxf.gcp-us-east1.cockroachlabs.cloud:26257/prueba?sslmode=verify-full"
        ),
        sslrootcert=os.path.join(app.static_folder, 'certs/root.crt')
    )
    return conn

@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route('/Home')
def home():
    return render_template('home.html')

@app.route('/Insertar', methods=['GET', 'POST'])
def insertar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        valor = request.form['valor']
        stock = request.form['stock']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO productos (nombre, valor_unitario, stock) VALUES (%s, %s, %s)",
                (nombre, float(valor), int(stock))
            )
            conn.commit()
            return redirect(url_for('registros'))
        except psycopg2.IntegrityError:
            conn.rollback()
            return render_template('insertar.html', error="⚠️ Error: El producto ya existe")
        finally:
            cur.close()
            conn.close()
    
    return render_template('insertar.html')

@app.route('/Comprar', methods=['GET', 'POST'])
def comprar():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        producto_id = request.form['producto']
        cantidad = int(request.form['cantidad'])
        
        cur.execute("SELECT stock FROM productos WHERE id = %s", (producto_id,))
        stock_actual = cur.fetchone()[0]
        
        if cantidad > stock_actual:
            cur.execute("SELECT * FROM productos")
            productos = cur.fetchall()
            cur.close()
            conn.close()
            return render_template('comprar.html', productos=productos, error="Stock insuficiente")
        
        cur.execute("UPDATE productos SET stock = stock - %s WHERE id = %s", (cantidad, producto_id))
        cur.execute("INSERT INTO ventas (producto_id, cantidad) VALUES (%s, %s)", (producto_id, cantidad))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('registros'))
    
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('comprar.html', productos=productos)

@app.route('/Registros')
def registros():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('registros.html', productos=productos)

@app.route('/Modificar/<producto_id>', methods=['GET', 'POST'])
def modificar(producto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        valor = request.form['valor']
        stock = request.form['stock']
        
        cur.execute(
            "UPDATE productos SET nombre = %s, valor_unitario = %s, stock = %s WHERE id = %s",
            (nombre, float(valor), int(stock), producto_id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('registros', actualizado=True))
    
    cur.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
    producto = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('modificar.html', producto=producto)

@app.route('/Eliminar/<producto_id>')
def eliminar(producto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM ventas WHERE producto_id = %s", (producto_id,))
        cur.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar: {str(e)}")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('registros'))

@app.route('/ReporteTotal')
def reporte_total():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.nombre, p.valor_unitario, p.stock, 
        SUM(v.cantidad) as total_vendido, 
        SUM(v.cantidad * p.valor_unitario) as total_ventas 
        FROM ventas v 
        JOIN productos p ON v.producto_id = p.id 
        GROUP BY p.id
    """)
    
    df = pd.DataFrame(cur.fetchall(), columns=['Producto', 'Valor Unitario', 'Stock Actual', 
                                             'Unidades Vendidas', 'Total Ventas'])
    df['Fecha'] = datetime.now().strftime("%Y-%m-%d")
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Reporte Total', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Reporte Total']
        
        header_format = workbook.add_format({
            'bold': True, 
            'bg_color': '#2c3e50', 
            'font_color': 'white',
            'border': 1
        })
        
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_format)
        
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 15, money_format)
        worksheet.set_column('C:E', 15)
        worksheet.set_column('F:F', 12)
    
    output.seek(0)
    return send_file(output, download_name='reporte_total.xlsx', as_attachment=True)

@app.route('/ReporteProducto/<producto_id>')
def reporte_producto(producto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.nombre, p.valor_unitario, p.stock,
        SUM(v.cantidad) as unidades_vendidas,
        SUM(v.cantidad * p.valor_unitario) as total_ventas,
        MAX(v.fecha_venta) as ultima_fecha
        FROM ventas v 
        JOIN productos p ON v.producto_id = p.id 
        WHERE p.id = %s
        GROUP BY p.id, p.nombre, p.valor_unitario, p.stock
    """, (producto_id,))
    
    df = pd.DataFrame(cur.fetchall(), columns=['Producto', 'Valor Unitario', 'Stock Actual',
                                              'Unidades Vendidas', 'Total Ventas', 'Última Fecha'])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Reporte Producto', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Reporte Producto']
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2c3e50',
            'font_color': 'white',
            'border': 1
        })
        
        money_format = workbook.add_format({'num_format': '$#,##0.00'})
        
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_format)
        
        worksheet.set_column('A:F', 15)
        worksheet.set_column('B:B', None, money_format)
        worksheet.set_column('E:E', None, money_format)
    
    output.seek(0)
    return send_file(output, download_name=f'reporte_{producto_id}.xlsx', as_attachment=True)

# Configuración para Vercel
if __name__ == "__vgi__":
    import serverless_wsgi
    handler = serverless_wsgi.handle_request(app)

if __name__ == '__main__':
    app.run(debug=True)