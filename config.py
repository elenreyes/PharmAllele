"""Ejecutar en el terminal scp u319418@formacio.bq.ub.edu:public_html y 
 luego poner el password que es dbw_2026
Para conectarte a la página:
    • ssh  u319418@formacio.bq.ub.edu
    • cd public_html
Para subir archivos 
    • scp archivo.html  u319418@formacio.bq.ub.edu:public_html/
Para borrar archivos:
    • rm -r archivo.html
Para verlo en local: python3 -m http.server 8000""" 

PREFIX = 'pharmallele'

# Conection with MySQL
MYSQL_USER = 'elenreyess'
MYSQL_PASSWORD = 'pharmAllele11!'
MYSQL_DB = 'mydb'
MYSQL_HOST = 'localhost'

SECRET_KEY = 'my_secret_key'
TITLE = 'My pharmacokinetic'