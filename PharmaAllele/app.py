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
usuario_personalizado = " "  
password_personalizado = " "      
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

@app.route('/buscar_drugs', methods=['GET','POST'])
def buscar_drug():
    # 1. Recogemos lo que el usuario escribió en el formulario
    termino = request.form.get('nombre_droga')
    
    # 2. Preparamos la consulta con LIKE para que encuentre coincidencias parciales
    # El % permite buscar si el nombre empieza, contiene o termina con ese texto
    query = text("SELECT * FROM drugs WHERE drug_name LIKE :nombre")
    
    # 3. Ejecutamos pasando el parámetro
    result = db.session.execute(query, {"nombre": f"%{termino}%"})
    
    columnas = result.keys()
    datos = [dict(zip(columnas, fila)) for fila in result.fetchall()]
    #datos = result.fetchall()
    
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


#6. 4º RUTA: BuSQUEDA farmaco - variantes asociadas 
@app.route('/drugs/<string:nombre_farmaco>')
def mostrar_detalles_drug(nombre_farmaco):
    # 1. Buscamos los datos del fármaco usando su nombre (PK)
    res_drug = db.session.execute(
        text("SELECT * FROM drugs WHERE drug_name = :nombre"), 
        {"nombre": nombre_farmaco}
    )
    info_droga = res_drug.fetchone()

    if not info_droga:
        return "Fármaco no encontrado", 404

    # 2. Buscamos sus variantes asociadas
    # He ajustado el JOIN asumiendo que tu tabla intermedia tiene 'drug_name' y 'variant_name'
    query_variantes = text("""
        SELECT v.* FROM variants v
        JOIN variants_has_drugs dv ON v.variant_name = dv.variants_variant_name
        WHERE dv.drugs_drug_name = :nombre
    """)
    res_variantes = db.session.execute(query_variantes, {"nombre": nombre_farmaco})
    listado_variantes = res_variantes.fetchall()

    return render_template(
        'detalles_drug.html', 
        droga=info_droga, 
        variantes=listado_variantes,
        title=f"Detalles de {nombre_farmaco}"
    )

#7. 5º RUTA: Busqueda DOBLE (Farmaco y variante a la vez)
@app.route('/search')
def search():
    # 1. Obtenemos los términos de búsqueda del formulario
    drug_query = request.args.get("drug", "").strip()
    variant_query = request.args.get("variant", "").strip()

    # 2. Construimos la consulta SQL con un JOIN
    # Buscamos en la tabla intermedia que conecta ambos
    sql = """
        SELECT dv.drugs_drug_name, dv.variants_variant_name, dv.phenotype_category_phenotype_category, dv.illness_illness_name, dv.evidence_category_evidence_category,dv.URL_web
        FROM variants_has_drugs dv
        JOIN variants v ON dv.variants_variant_name = v.variant_name
        WHERE 1=1
    """
    
    params = {}
    
    # 3. Añadimos filtros dinámicamente según lo que el usuario rellene
    if drug_query:
        sql += " AND dv.drugs_drug_name LIKE :drug"
        params["drug"] = f"%{drug_query}%"
    
    if variant_query:
        sql += " AND dv.variants_variant_name LIKE :variant"
        params["variant"] = f"%{variant_query}%"

    # 4. Ejecutamos
    result = db.session.execute(text(sql), params)
    columnas = result.keys()
    # Convertimos a lista de diccionarios como le gusta a tu profesor
    results = [dict(zip(columnas, fila)) for fila in result.fetchall()]

    return render_template("results.html", results=results, drug=drug_query, variant=variant_query)


#7. 6º RUTA: Busqueda de Evidence-Category
@app.route("/evidence/<string:category_name>")
def detalle_evidencia(category_name):
    # 1. Buscamos la descripción en la tabla 'evidence_category'
    # Ajusta los nombres de las columnas ('category' y 'description') a los tuyos
    query = text("""
        SELECT evidence_category, evidence_description 
        FROM evidence_category 
        WHERE evidence_category = :cat
    """)
    result = db.session.execute(query, {"cat": category_name})
    info_evidencia = result.fetchone()

    if not info_evidencia:
        return "Categoría de evidencia no encontrada", 404

    return render_template("detalles_evidencia.html", evidencia=info_evidencia)

#La app va encima de esto
if __name__ == '__main__':
    app.run(debug=True)
