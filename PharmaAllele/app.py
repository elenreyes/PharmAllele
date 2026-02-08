import os
import sys
import re
import uuid
import subprocess

from flask import Flask, render_template, session, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# 1. Crear la APP
app = Flask(__name__)

# 1.2 Configuración de los datos de acceso
usuario_personalizado = "web_admin"  
password_personalizado = "R4di4dor"      
host = "localhost"
database = "mydb"

# 2. Conexión a TU base de datos 'mydb'
# Pon tu contraseña real de MySQL aquí
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{usuario_personalizado}:{password_personalizado}@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TITLE'] = 'Mi Farmacogenética'

db = SQLAlchemy(app)

# 3. Tu primera RUTA (La página de inicio)
@app.route('/')
def index():
    # Vamos a contar cuántos genes tienes para saber si funciona
    result = db.session.execute(text("SELECT COUNT(*) FROM gene"))
    total = result.fetchone()[0]
    
    return render_template('index.html', cantidad=total)

# 4. 2º RUTA: BUSCAR DRUGS
@app.route('/drugs')
def listar_drugs():
    # 1. Hacemos la consulta a la tabla 'drug'
    # Nota: Asegúrate de que en tu MySQL la tabla se llame 'drugs'
    result = db.session.execute(text("SELECT * FROM drugs LIMIT 100"))
    #CONSEJO: Si la tabla drug tiene miles de filas, el navegador podría tardar un poco en cargar. 
    # Si ves que tarda mucho, puedes cambiar la consulta a SELECT * FROM drug LIMIT 100 para probar.

    # 2. Obtenemos los nombres de las columnas para la cabecera de la tabla
    columnas = result.keys()
    
    # 3. Obtenemos todas las filas
    datos = result.fetchall()
    
    # 4. Enviamos todo al nuevo HTML
    return render_template('drugs.html', columnas=columnas, filas=datos, title="Listado de Fármacos")

@app.route('/buscar_drugs', methods=['POST'])
def buscar_drug():
    # 1. Recogemos lo que el usuario escribió en el formulario
    termino = request.form.get('nombre_droga')
    
    # 2. Preparamos la consulta con LIKE para que encuentre coincidencias parciales
    # El % permite buscar si el nombre empieza, contiene o termina con ese texto
    query = text("SELECT * FROM drugs WHERE drug_name LIKE :nombre")
    
    # 3. Ejecutamos pasando el parámetro
    result = db.session.execute(query, {"nombre": f"%{termino}%"})
    
    columnas = result.keys()
    datos = result.fetchall()
    
    # 4. Reutilizamos el mismo HTML de la tabla para mostrar el resultado
    return render_template('drugs.html', columnas=columnas, filas=datos, title=f"Resultados para: {termino}")

#5. 3º RUTA: BUSCAR GENES
@app.route('/buscar_genes', methods=['POST'])
def buscar_gene():
    termino = request.form.get('nombre_gen')
    query = text("SELECT * FROM gene WHERE gene_name LIKE :nombre")
    result = db.session.execute(query, {"nombre": f"%{termino}%"})
    columnas = result.keys()
    datos = result.fetchall()
    return render_template('genes.html', columnas=columnas, filas=datos, title=f"Resultados para: {termino}")


#La app va encima de esto
if __name__ == '__main__':
    app.run(debug=True)