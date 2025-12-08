# cliente.py
"""
Modelo para la tabla clientes de la base de datos ybook
"""
from .conexion import conexion_bd

class Cliente:
    @staticmethod
    def agregar(nombre, telefono=None, notas=None, empleado=False):
        db = conexion_bd()
        query = """
            INSERT INTO clientes (nombre, telefono, notas, empleado)
            VALUES (%s, %s, %s, %s)
        """
        db.ejecutar(query, (nombre, telefono, notas, empleado))

    @staticmethod
    def buscar_por_nombre(nombre):
        db = conexion_bd()
        query = "SELECT * FROM clientes WHERE nombre LIKE %s"
        return db.consultar(query, (f"%{nombre}%",))

    @staticmethod
    def obtener_por_id(id_cliente):
        db = conexion_bd()
        query = "SELECT * FROM clientes WHERE id_cliente = %s"
        resultados = db.consultar(query, (id_cliente,))
        return resultados[0] if resultados else None

    @staticmethod
    def obtener_todos():
        db = conexion_bd()
        query = "SELECT * FROM clientes"
        return db.consultar(query)

    @staticmethod
    def obtener_empleados():
        db = conexion_bd()
        query = "SELECT id_cliente, nombre FROM clientes WHERE empleado = 1"
        return db.consultar(query)

    @staticmethod
    def obtener_nombre_por_id(id_cliente):
        db = conexion_bd()
        query = "SELECT nombre FROM clientes WHERE id_cliente = %s"
        resultados = db.consultar(query, (id_cliente,))
        if resultados:
            return resultados[0]['nombre']
        return None
    
    @staticmethod
    def es_empleado(id_cliente):
        db = conexion_bd()
        query = "SELECT empleado FROM clientes WHERE id_cliente = %s"
        resultado = db.consultar(query, (id_cliente,))
        
        if not resultado:
            return False  # Si no existe el cliente, asumimos que no es empleado
        
        return bool(resultado[0]['empleado'])
