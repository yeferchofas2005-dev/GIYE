from modelo.conexion import conexion_bd

class Filtros:

    @staticmethod
    def filtrar_por_fecha(fecha):
        db = conexion_bd()

        transacciones_filtradas = []

        query = "SELECT * FROM transacciones WHERE DATE(fecha_creacion) = %s"
        resultados = db.consultar(query, (fecha,))

        transacciones_filtradas.extend(resultados)
        return transacciones_filtradas
    
    @staticmethod
    def filtrar_por_nombre_cliente(nombre_cliente):
        db = conexion_bd()

        transacciones_filtradas = []

        query = "SELECT t.* FROM transacciones t JOIN clientes c ON t.id_cliente = c.id_cliente WHERE c.nombre LIKE %s"
        resultados = db.consultar(query, (f"%{nombre_cliente}%",))
        
        transacciones_filtradas.extend(resultados)
        return transacciones_filtradas

    @staticmethod
    def filtrar_por_orden_alfabetico(ascendente=True):
        db = conexion_bd()

        transacciones_filtradas = []

        orden = "ASC" if ascendente else "DESC"
        query = f"""
            SELECT t.* FROM transacciones t
            JOIN clientes c ON t.id_cliente = c.id_cliente
            ORDER BY c.nombre {orden}
        """
        resultados = db.consultar(query)

        transacciones_filtradas.extend(resultados)
        return transacciones_filtradas
    
    @staticmethod
    def filtrar_por_deuda_menor_o_mayor(mayor=True):
        db = conexion_bd()
        orden = "DESC" if mayor else "ASC"

        query = f"""
            SELECT * FROM transacciones
            WHERE tipo_transaccion = 'DEUDA'
            ORDER BY monto {orden}
        """
        return db.consultar(query)

    @staticmethod
    def filtrar_por_abono_menor_o_mayor(mayor=True):
        db = conexion_bd()
        orden = "DESC" if mayor else "ASC"

        query = f"""
            SELECT * FROM transacciones
            WHERE tipo_transaccion = 'INGRESO'
            ORDER BY monto {orden}
        """
        return db.consultar(query)

    @staticmethod
    def filtrar_por_estado_deuda(estado):
        db = conexion_bd()

        if estado == "Todas":
            query = "SELECT * FROM transacciones"
            return db.consultar(query)

        if estado == "Tachadas":  # CANCELADAS
            query = "SELECT * FROM transacciones WHERE estado_deuda = 'CANCELADA'"
            return db.consultar(query)

        if estado == "Sin tachar":  # SOLO PENDIENTES
            query = "SELECT * FROM transacciones WHERE estado_deuda = 'PENDIENTE'"
            return db.consultar(query)
