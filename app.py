#------------------------------------------------------------
# Instalar Flask
from flask import Flask, request, jsonify

# Instalar Flask-cors

from flask_cors import CORS

# Instalar MYSQL

import mysql.connector

# Instalar Werkzeug

from werkzeug.utils import secure_filename

# Importar 

import os
import time

#---------------------------------------------------------

app = Flask(__name__)
CORS(app)

#---------------------------------------------------------

class Catalogo:
    #---------------------------------------------------------
    # Constructor de la clase e inicio con MySQL -------------
    #---------------------------------------------------------

    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        # Intenta seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err
            
        self.cursor.execute(('''CREATE TABLE IF NOT EXISTS productos ( 
            codigo INT AUTO_INCREMENT PRIMARY KEY, 
            descripcion VARCHAR(255) NOT NULL,
            cantidad INT NOT NULL,
            precio DECIMAL(10, 2) NOT NULL,
            imagen_url VARCHAR(255))'''))
        self.conn.commit()

        # Cierra el cursos inicial y abre uno nuevo con el parámetro dictionary = True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)
        
#-------------------------------------------------
# INICIA EL DESARROLLO DE LA BASE DE DATOS -------
#-------------------------------------------------

# Define una lista para almacenar los productos
productos = []

# Agregar un producto (create)

def agregar_producto(self, descripcion, cantidad, precio, imagen):

    sql = "INSERT INTO productos (descripcion, cantidad, precio, imagen_url) VALUES (%s,%s,%s,%s)"
    valores = (descripcion, cantidad, precio, imagen)
    self.cursor.execute(sql, valores)
    self.conn.commit()
    return self.cursor.lastrowid

# Consulta el código del producto

def consultar_producto(self, codigo):
    self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
    return self.cursor.fetchone()
    
# Modifica un producto

def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor):
        sql = "UPDATE productos SET descripcion = %s, cantidad = %s, precio = %s, imagen_url = %s, WHERE codigo = %s"
        valores = (nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

# Mostrar por pantalla las caracteristicas del producto

def mostrar_producto(self, codigo):
    producto = self.consultar_producto(codigo)
    if producto:
        print("-" * 50)
        print(f"Codigo.....: {producto['codigo']}")
        print(f"Descripcion: {producto['descripcion']}")
        print(f"Cantidad...: {producto['cantidad']}")
        print(f"Precio.....: {producto['precio']}")
        print(f"Imagen.....: {producto['imagen']}")
        print("-" * 50)
    else:
        print("Producto no encontrado.")

# Muestra la lista de productos

def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        productos = self.cursor.fetchall()
        return productos

# Eliminar producto

def eliminar_producto(self, codigo):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM productos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0
    
#---------------------------------------------------------
# Cuerpo del programa ------------------------------------
#---------------------------------------------------------

catalogo = Catalogo(host='briangfunes.mysql.pythonanywhere-services.com', user='briangfunes', password='', database='briangfunes$default')

# Carpeta para guardar imagenes
#ruta_destino = './static/imagenes/'

ruta_destino = '/home/briangfunes/static/imagenes/'

@app.route("/productos", methods=["GET"])
def listar_productos():
    productos = catalogo.listar_productos()
    return jsonify(productos)

@app.route("/productos/<int:codigo>", methods=["GET"])
def mostrar_producto(codigo):
    producto = catalogo.consultar_producto(codigo)
    if producto:
        return jsonify(producto)
    else:
        return "Producto no encontrado", 404
    
@app.route("/productos", methods=["POST"])
def agregar_producto():
    #Recojo los datos del form
    descripcion = request.form['descripcion']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    imagen = request.files['imagen']
    proveedor = request.form['proveedor']  
    nombre_imagen = ""

    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen) 
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

    nuevo_codigo = catalogo.agregar_producto(descripcion, cantidad, precio, nombre_imagen, proveedor)
    if nuevo_codigo:    
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        return jsonify({"mensaje": "Producto agregado correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        return jsonify({"mensaje": "Error al agregar el producto."}), 500

@app.route("/productos/<int:codigo>", methods=["PUT"])
def modificar_producto(codigo):
    #Se recuperan los nuevos datos del formulario
    nueva_descripcion = request.form.get("descripcion")
    nueva_cantidad = request.form.get("cantidad")
    nuevo_precio = request.form.get("precio")
    nuevo_proveedor = request.form.get("proveedor")
    
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) 
        nombre_base, extension = os.path.splitext(nombre_imagen) 
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" 

        # Guardar la imagen en el servidor
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        
        # Busco el producto guardado
        producto = catalogo.consultar_producto(codigo)
        if producto: # Si existe el producto...
            imagen_vieja = producto["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(ruta_destino, imagen_vieja)

            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    else:     
        producto = catalogo.consultar_producto(codigo)
        if producto:
            nombre_imagen = producto["imagen_url"]

   # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if catalogo.modificar_producto(codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nombre_imagen, nuevo_proveedor):
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 403

@app.route("/productos/<int:codigo>", methods=["DELETE"])
def eliminar_producto(codigo):
    # Primero, obtiene la información del producto para encontrar la imagen
    producto = catalogo.consultar_producto(codigo)
    if producto:
        # Eliminar la imagen asociada si existe
        ruta_imagen = os.path.join(ruta_destino, producto['imagen_url'])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

        # Luego, elimina el producto del catálogo
        if catalogo.eliminar_producto(codigo):
            return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True)