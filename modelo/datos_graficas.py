from modelo.conexion import conexion_bd

class datos_graficas:
    """
    Modelo encargado EXCLUSIVAMENTE de obtener datos estadísticos
    (agregaciones, agrupaciones, métricas).
    """

    # ---------------------------------------------------------
    # CLIENTES CON MAYOR DEUDA
    # ---------------------------------------------------------
    @staticmethod
    def obtener_clientes_con_mayor_deuda(limite=10):
        db = conexion_bd()

        query = """
            SELECT 
                c.nombre AS cliente,
                SUM(t.monto) AS total_deuda
            FROM transacciones t
            JOIN clientes c ON t.id_cliente = c.id_cliente
            WHERE 
                t.tipo_transaccion = 'DEUDA'
                AND t.estado_deuda = 'PENDIENTE'
            GROUP BY c.id_cliente
            ORDER BY total_deuda DESC
            LIMIT %s
        """

        resultados = db.consultar(query, (limite,))

        return [
            {
                "cliente": r["cliente"],
                "total_deuda": float(r["total_deuda"])
            }
            for r in resultados
        ]

    # ---------------------------------------------------------
    # TOTAL DE DEUDAS VS ABONOS
    # ---------------------------------------------------------
    @staticmethod
    def obtener_total_deudas_y_abonos():
        db = conexion_bd()

        query = """
            SELECT 
                tipo_transaccion,
                SUM(monto) AS total
            FROM transacciones
            GROUP BY tipo_transaccion
        """

        resultados = db.consultar(query)

        totales = {"DEUDA": 0, "INGRESO": 0}

        for r in resultados:
            totales[r["tipo_transaccion"]] = float(r["total"])

        return totales

    # ---------------------------------------------------------
    # LISTA DE DEUDAS MÁS ANTIGUAS
    # ---------------------------------------------------------
    @staticmethod
    def obtener_lista_deudas_mas_antiguas(limite=10):
        db = conexion_bd()

        query = """
            SELECT 
                c.nombre AS cliente,
                t.fecha_creacion,
                t.monto
            FROM transacciones t
            JOIN clientes c ON t.id_cliente = c.id_cliente
            WHERE 
                t.tipo_transaccion = 'DEUDA'
                AND t.estado_deuda = 'PENDIENTE'
            ORDER BY t.fecha_creacion ASC
            LIMIT %s
        """

        resultados = db.consultar(query, (limite,))

        return [
            {
                "cliente": r["cliente"],
                "fecha": r["fecha_creacion"].strftime("%Y-%m-%d"),
                "monto": float(r["monto"])
            }
            for r in resultados
        ]

    # ---------------------------------------------------------
    # DEUDA Y ABONO POR MES
    # ---------------------------------------------------------
    @staticmethod
    def obtener_transacciones_por_mes():
        db = conexion_bd()

        query = """
            SELECT
                DATE_FORMAT(fecha_creacion, '%Y-%m') AS mes,
                tipo_transaccion,
                SUM(monto) AS total
            FROM transacciones
            GROUP BY mes, tipo_transaccion
            ORDER BY mes ASC
        """

        resultados = db.consultar(query)

        resumen = {}

        for r in resultados:
            mes = r["mes"]
            if mes not in resumen:
                resumen[mes] = {"mes": mes, "deuda": 0, "abono": 0}

            if r["tipo_transaccion"] == "DEUDA":
                resumen[mes]["deuda"] = float(r["total"])
            else:
                resumen[mes]["abono"] = float(r["total"])

        return list(resumen.values())
