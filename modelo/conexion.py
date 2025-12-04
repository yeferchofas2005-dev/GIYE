# conexion.py
import mysql.connector

class conexion_bd:

    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = '1074129082'
        self.database = 'ybook'
        self.conn = None
        self.cursor = None
    
#--- Metodos de manejo de la base de datos ---

    #Metodo para probar la conexion a la base de datos.
    def probar_conexion(self):
        try:
            self.conectar()
            print("Conexión exitosa a la base de datos.")
            self.cerrar()
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
    
    #Metodo para conectar a la base de datos
    def conectar(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor(dictionary=True)

    #Metodo para cerrar la conexion a la base de datos
    def cerrar(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    #Metodo para ejecutar un query (insert, update, delete)
    def ejecutar(self, query, params=None):
        self.conectar()
        self.cursor.execute(query, params or ())
        self.conn.commit()
        self.cerrar()

    #Metodo para ejecutar un query de seleccion (select)
    def consultar(self, query, params=None):
        self.conectar()
        self.cursor.execute(query, params or ())
        resultados = self.cursor.fetchall()
        self.cerrar()
        return resultados