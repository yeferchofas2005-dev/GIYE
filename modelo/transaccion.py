# transaccion.py
"""
Modelo para la tabla transacciones de la base de datos ybook
"""
from .conexion import conexion_bd
from datetime import datetime

class Transaccion:

    @staticmethod
    
    def agregar(fecha_creacion, tipo_transaccion, subtipo_transaccion, monto, id_cliente, id_empleado, descripcion=None, referencia_original=None, saldo_afectado=0, estado_deuda='PENDIENTE'):

        db = conexion_bd()

        if fecha_creacion is None:
            fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        query = """
            INSERT INTO transacciones (
                fecha_creacion, tipo_transaccion, subtipo_transaccion,
                monto, id_cliente, id_empleado,
                descripcion, referencia_original,
                saldo_afectado, estado_deuda
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        db.ejecutar(query, (fecha_creacion, tipo_transaccion, subtipo_transaccion, monto, id_cliente, id_empleado, descripcion, referencia_original, saldo_afectado, estado_deuda))

    @staticmethod
    def obtener_por_id(id_transaccion):
        db = conexion_bd()
        query = "SELECT * FROM transacciones WHERE id_transaccion = %s"
        resultados = db.consultar(query, (id_transaccion,))
        return resultados[0] if resultados else None
    
    @staticmethod
    def obtener_por_cliente(id_cliente):
        db = conexion_bd()
        query = "SELECT * FROM transacciones WHERE id_cliente = %s ORDER BY fecha_creacion DESC"
        return db.consultar(query, (id_cliente,))

    @staticmethod
    def obtener_todas():
        db = conexion_bd()
        query = "SELECT * FROM transacciones ORDER BY fecha_creacion DESC"
        resultados = db.consultar(query)
        return resultados

    @staticmethod
    def actualizar_estado(id_transaccion, nuevo_estado):
        db = conexion_bd()
        query = "UPDATE transacciones SET estado_deuda = %s WHERE id_transaccion = %s"
        db.ejecutar(query, (nuevo_estado, id_transaccion))
