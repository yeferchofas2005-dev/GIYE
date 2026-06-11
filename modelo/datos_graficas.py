from modelo.conexion import conexion_bd
from datetime import datetime, timedelta

class datos_graficas:
    """
    Modelo encargado EXCLUSIVAMENTE de obtener datos estadísticos
    (agregaciones, agrupaciones, métricas).

    MÉTODOS DISPONIBLES:
    --------------------
    - obtener_clientes_con_mayor_deuda     : Top clientes con más deuda pendiente
    - obtener_total_deudas_y_abonos        : Totales globales DEUDA vs INGRESO
    - obtener_lista_deudas_mas_antiguas    : Deudas pendientes más antiguas con días transcurridos
    - obtener_transacciones_por_mes        : Resumen mensual agrupado por tipo
    - obtener_resumen_hoy                  : KPIs del día actual (caja, nequi, deudas, pagos)
    - obtener_rendimiento_por_empleado     : Cuánto fió cada empleado y cuánto se recuperó
    - obtener_flujo_semanal                : Entradas vs deudas nuevas de los últimos 7 días
    - obtener_clientes_riesgosos           : Clientes con deudas antiguas sin ningún pago reciente
    """

    # ---------------------------------------------------------
    # CLIENTES CON MAYOR DEUDA
    # ---------------------------------------------------------
    @staticmethod
    def obtener_clientes_con_mayor_deuda(limite=10):
        """
        Retorna los clientes con mayor monto de deuda PENDIENTE acumulada.
        Excluye empleados y solo considera deudas no canceladas.
        """
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
                AND c.empleado = FALSE
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
        """
        Retorna el total acumulado histórico de DEUDA vs INGRESO.
        Usado para la gráfica de pastel global.
        """
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
        """
        Retorna las deudas PENDIENTE más antiguas ordenadas por fecha ASC.
        Incluye la cantidad de días que llevan sin pagarse para
        que el dueño priorice a quién cobrarle primero.
        """
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
        hoy = datetime.now()

        return [
            {
                "cliente": r["cliente"],
                "fecha": r["fecha_creacion"].strftime("%Y-%m-%d"),
                "monto": float(r["monto"]),
                "dias": (hoy - r["fecha_creacion"]).days
            }
            for r in resultados
        ]

    # ---------------------------------------------------------
    # DEUDA Y ABONO POR MES
    # ---------------------------------------------------------
    @staticmethod
    def obtener_transacciones_por_mes():
        """
        Retorna un resumen mensual agrupado por tipo de transacción.
        Permite visualizar la tendencia del negocio mes a mes.
        """
        db = conexion_bd()

        query = """
            SELECT
                DATE_FORMAT(fecha_creacion, '%%Y-%%m') AS mes,
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

    # ---------------------------------------------------------
    # RESUMEN DEL DÍA DE HOY
    # ---------------------------------------------------------
    @staticmethod
    def obtener_resumen_hoy():
        """
        Retorna los KPIs del día actual:
        - Total ingresado por caja (efectivo)
        - Total ingresado por Nequi
        - Cantidad y monto de deudas nuevas creadas hoy
        - Cantidad de deudas pagadas hoy

        Útil para el dueño que revisa el panel todos los días
        y necesita saber cómo cerró el día de un vistazo.
        """
        db = conexion_bd()
        hoy = datetime.now().strftime("%Y-%m-%d")

        # Ingresos del día separados por subtipo
        query_ingresos = """
            SELECT
                subtipo_transaccion,
                SUM(monto) AS total
            FROM transacciones
            WHERE
                tipo_transaccion = 'INGRESO'
                AND DATE(fecha_creacion) = %s
            GROUP BY subtipo_transaccion
        """

        # Deudas nuevas creadas hoy
        query_deudas_nuevas = """
            SELECT COUNT(*) AS cantidad, COALESCE(SUM(monto), 0) AS total
            FROM transacciones
            WHERE
                tipo_transaccion = 'DEUDA'
                AND DATE(fecha_creacion) = %s
        """

        # Deudas pagadas hoy (canceladas hoy, sin importar cuándo se crearon)
        query_pagadas_hoy = """
            SELECT COUNT(*) AS cantidad
            FROM transacciones
            WHERE
                tipo_transaccion = 'DEUDA'
                AND estado_deuda = 'CANCELADA'
                AND DATE(fecha_creacion) = %s
        """

        ingresos = db.consultar(query_ingresos, (hoy,))
        deudas_nuevas = db.consultar(query_deudas_nuevas, (hoy,))
        pagadas_hoy = db.consultar(query_pagadas_hoy, (hoy,))

        subtipos_nequi = {"NEQUI", "NEQUI_RECIBIDO", "PAGO_NEQUI"}

        total_caja  = 0
        total_nequi = 0

        for r in ingresos:
            if r["subtipo_transaccion"] in subtipos_nequi:
                total_nequi += float(r["total"])
            else:
                total_caja += float(r["total"])

        return {
            "total_caja":        total_caja,
            "total_nequi":       total_nequi,
            "deudas_nuevas":     int(deudas_nuevas[0]["cantidad"]) if deudas_nuevas else 0,
            "monto_deudas_hoy":  float(deudas_nuevas[0]["total"])  if deudas_nuevas else 0,
            "deudas_pagadas":    int(pagadas_hoy[0]["cantidad"])    if pagadas_hoy   else 0,
        }

    # ---------------------------------------------------------
    # RENDIMIENTO POR EMPLEADO
    # ---------------------------------------------------------
    @staticmethod
    def obtener_rendimiento_por_empleado():
        """
        Retorna por cada empleado:
        - Cuánto ha fiado en total (deudas que registró)
        - Cuánto de eso se ha recuperado (deudas canceladas)
        - Porcentaje de recuperación

        Permite al dueño detectar si algún empleado está fiando
        de forma irresponsable o a clientes que no pagan.
        """
        db = conexion_bd()

        query = """
            SELECT
                c.nombre AS empleado,
                SUM(t.monto) AS total_fiado,
                SUM(CASE WHEN t.estado_deuda = 'CANCELADA' THEN t.monto ELSE 0 END) AS total_recuperado
            FROM transacciones t
            JOIN clientes c ON t.id_empleado = c.id_cliente
            WHERE
                t.tipo_transaccion = 'DEUDA'
                AND c.empleado = TRUE
            GROUP BY c.id_cliente
            ORDER BY total_fiado DESC
        """

        resultados = db.consultar(query)

        return [
            {
                "empleado":          r["empleado"],
                "total_fiado":       float(r["total_fiado"]),
                "total_recuperado":  float(r["total_recuperado"]),
                "porcentaje":        round(
                    float(r["total_recuperado"]) / float(r["total_fiado"]) * 100, 1
                ) if float(r["total_fiado"]) > 0 else 0
            }
            for r in resultados
        ]

    # ---------------------------------------------------------
    # FLUJO SEMANAL (ÚLTIMOS 7 DÍAS)
    # ---------------------------------------------------------
    @staticmethod
    def obtener_flujo_semanal():
        """
        Retorna los movimientos de los últimos 7 días agrupados por día:
        - Total ingresado (caja + nequi)
        - Total en deudas nuevas

        Permite ver de un vistazo si la semana va bien o mal
        y detectar días con mucho fiado sin recuperación.
        """
        db = conexion_bd()

        query = """
            SELECT
                DATE(fecha_creacion) AS dia,
                tipo_transaccion,
                SUM(monto) AS total
            FROM transacciones
            WHERE fecha_creacion >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY dia, tipo_transaccion
            ORDER BY dia ASC
        """

        resultados = db.consultar(query)

        # construir los 7 días aunque no tengan movimientos
        hoy = datetime.now().date()
        dias = {
            (hoy - timedelta(days=i)).strftime("%Y-%m-%d"): {"dia": (hoy - timedelta(days=i)).strftime("%d/%m"), "ingreso": 0, "deuda": 0}
            for i in range(6, -1, -1)
        }

        for r in resultados:
            dia_key = r["dia"].strftime("%Y-%m-%d")
            if dia_key in dias:
                if r["tipo_transaccion"] == "INGRESO":
                    dias[dia_key]["ingreso"] = float(r["total"])
                else:
                    dias[dia_key]["deuda"] = float(r["total"])

        return list(dias.values())

    # ---------------------------------------------------------
    # CLIENTES RIESGOSOS
    # ---------------------------------------------------------
    @staticmethod
    def obtener_clientes_riesgosos(dias_sin_pagar=30, limite=10):
        """
        Retorna clientes que acumulan deuda pendiente y llevan
        más de `dias_sin_pagar` días sin registrar ningún pago.

        Un cliente riesgoso no es necesariamente el que más debe,
        sino el que debe hace tiempo y no muestra señales de pagar.

        Parámetros:
        -----------
        dias_sin_pagar (int): umbral de días para considerar riesgoso (default 30)
        limite (int): máximo de registros a retornar
        """
        db = conexion_bd()

        query = """
            SELECT
                c.nombre AS cliente,
                SUM(t.monto) AS total_pendiente,
                MIN(t.fecha_creacion) AS deuda_mas_antigua,
                DATEDIFF(NOW(), MIN(t.fecha_creacion)) AS dias_sin_pagar
            FROM transacciones t
            JOIN clientes c ON t.id_cliente = c.id_cliente
            WHERE
                t.tipo_transaccion = 'DEUDA'
                AND t.estado_deuda = 'PENDIENTE'
                AND c.empleado = FALSE
                AND NOT EXISTS (
                    SELECT 1 FROM transacciones t2
                    WHERE t2.id_cliente = t.id_cliente
                      AND t2.tipo_transaccion = 'INGRESO'
                      AND t2.fecha_creacion >= DATE_SUB(NOW(), INTERVAL %s DAY)
                )
            GROUP BY c.id_cliente
            HAVING dias_sin_pagar >= %s
            ORDER BY dias_sin_pagar DESC
            LIMIT %s
        """

        resultados = db.consultar(query, (dias_sin_pagar, dias_sin_pagar, limite))

        return [
            {
                "cliente":          r["cliente"],
                "total_pendiente":  float(r["total_pendiente"]),
                "dias_sin_pagar":   int(r["dias_sin_pagar"]),
                "desde":            r["deuda_mas_antigua"].strftime("%Y-%m-%d")
            }
            for r in resultados
        ]