import pandas as pd
from modelo.conexion import conexion_bd
from datetime import datetime, time

class gestion_archivos:
    """
    Clase encargada de la generación y exportación de archivos del sistema.

    RESPONSABILIDAD GENERAL:
    ------------------------
    - Consultar información almacenada en la base de datos
    - Transformar los resultados en estructuras tabulares (DataFrame)
    - Exportar la información a archivos Excel (.xlsx)
    - Retornar la ruta del archivo generado para su uso posterior
      (por ejemplo, envío por correo o almacenamiento)

    CONTEXTO:
    ---------
    Esta clase es utilizada principalmente por:
    - El módulo de backups
    - Envío de correos con archivos adjuntos
    - Procesos de exportación de información del sistema

    NOTAS DE DISEÑO:
    ----------------
    - No contiene lógica de interfaz gráfica
    - No envía correos
    - No decide rutas dinámicamente fuera de su responsabilidad
    - Cumple con el principio de responsabilidad única (SRP)
    """

    def guardar_datos_clientes_excel(self):
        """
        Genera un archivo Excel con el listado completo de clientes.

        RESPONSABILIDAD:
        -----------------
        - Consultar todos los registros de la tabla `clientes`
        - Convertir los datos en un DataFrame de pandas
        - Exportar los datos a un archivo Excel
        - Retornar la ruta del archivo generado

        RETORNA:
        --------
        str:
            Ruta del archivo Excel generado (clientes.xlsx)

        FLUJO:
        ------
        1. Define la ruta de salida del archivo
        2. Abre conexión a la base de datos
        3. Ejecuta una consulta SELECT sobre la tabla clientes
        4. Convierte los resultados a un DataFrame
        5. Guarda el DataFrame como archivo Excel
        6. Retorna la ruta para su posterior uso

        NOTAS:
        ------
        - El archivo se sobrescribe si ya existe
        - El Excel no incluye índices del DataFrame
        """

        ruta = "Data/clientes.xlsx"

        bd = conexion_bd()
        usuarios = bd.consultar("SELECT * FROM clientes")

        df = pd.DataFrame(usuarios)
        df.to_excel(ruta, index=False)

        return ruta

    def guardar_datos_transacciones_excel(self):
        """
        Genera un archivo Excel con el listado completo de transacciones.

        RESPONSABILIDAD:
        -----------------
        - Consultar todas las transacciones del sistema
        - Exportar los datos a un archivo Excel
        - Retornar la ruta del archivo generado

        RETORNA:
        --------
        str:
            Ruta del archivo Excel generado (transacciones.xlsx)

        FLUJO:
        ------
        1. Define la ruta del archivo
        2. Consulta todos los registros de la tabla transacciones
        3. Convierte los datos en DataFrame
        4. Exporta el DataFrame a Excel
        5. Retorna la ruta

        NOTAS:
        ------
        - Útil para backups generales
        - El archivo se genera completo sin filtros
        """

        ruta = "Data/transacciones.xlsx"

        bd = conexion_bd()
        transacciones = bd.consultar("SELECT * FROM transacciones")

        df = pd.DataFrame(transacciones)
        df.to_excel(ruta, index=False)

        return ruta

    def guardar_datos_transacciones_excel_por_fecha(self, fecha_inicio, fecha_fin):
        """
        Genera un archivo Excel con las transacciones filtradas por rango de fechas.

        RESPONSABILIDAD:
        -----------------
        - Consultar transacciones entre dos fechas específicas
        - Generar un archivo Excel con nombre dinámico según el rango
        - Retornar la ruta del archivo generado

        PARÁMETROS:
        -----------
        fecha_inicio (str | date):
            Fecha inicial del rango de consulta

        fecha_fin (str | date):
            Fecha final del rango de consulta

        RETORNA:
        --------
        str:
            Ruta del archivo Excel generado con transacciones filtradas

        FLUJO:
        ------
        1. Construye una ruta de archivo con el rango de fechas
        2. Ejecuta una consulta SQL con filtro BETWEEN
        3. Convierte los resultados a DataFrame
        4. Exporta los datos a Excel
        5. Retorna la ruta del archivo

        NOTAS:
        ------
        - El nombre del archivo incluye las fechas seleccionadas
        - Ideal para backups manuales por período
        - Se asume que las fechas son válidas y compatibles con la BD
        """

        ruta = f"Data/transacciones_por_fecha_{fecha_inicio}_{fecha_fin}.xlsx"

        # Ajustar fechas para cubrir TODO el día
        fecha_inicio_dt = datetime.combine(fecha_inicio, time.min)
        fecha_fin_dt = datetime.combine(fecha_fin, time.max)

        db = conexion_bd()
        query = """
        SELECT * FROM transacciones
        WHERE fecha_creacion BETWEEN %s AND %s
        """
        transacciones = db.consultar(query, (fecha_inicio_dt, fecha_fin_dt))

        df = pd.DataFrame(transacciones)
        df.to_excel(ruta, index=False)

        return ruta

    def importar_clientes(self, ruta_excel):
        """
        Importa clientes desde un archivo Excel usando id_cliente como
        criterio de duplicidad.

        RESPONSABILIDAD:
        -----------------
        - Insertar solo clientes cuyo id_cliente NO exista en la BD
        - Ignorar automáticamente los duplicados por PRIMARY KEY

        PARÁMETROS:
        -----------
        ruta_excel (str):
            Ruta del archivo Excel

        """

        df = pd.read_excel(ruta_excel)

        db = conexion_bd()

        query = """
        INSERT IGNORE INTO clientes (id_cliente, nombre, telefono, notas, empleado)
        VALUES (%s, %s, %s, %s, %s)
        """

        for _, fila in df.iterrows():
            db.ejecutar(query, (
                int(fila["id_cliente"]),
                fila["nombre"],
                fila["telefono"],
                fila.get("notas"),
                fila.get("empleado")
            ))
    
    def importar_transacciones(self, ruta_excel):
        """
        Importa transacciones desde un archivo Excel usando id_transaccion
        como criterio de duplicidad.

        RESPONSABILIDAD:
        -----------------
        - Insertar solo transacciones cuyo id_transaccion NO exista en la BD
        - Ignorar automáticamente los duplicados por PRIMARY KEY

        PARÁMETROS:
        -----------
        ruta_excel (str):
            Ruta del archivo Excel

        """

        df = pd.read_excel(ruta_excel)

        db = conexion_bd()

        query = """
        INSERT IGNORE INTO transacciones (
            id_transaccion,
            fecha_creacion,
            tipo_transaccion,
            subtipo_transaccion,
            monto,
            id_cliente,
            descripcion,
            referencia_original,
            saldo_afectado,
            estado_deuda,
            id_empleado
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for _, fila in df.iterrows():
            def limpiar(valor):
                return None if pd.isna(valor) else valor

            db.ejecutar(query, (
                int(fila["id_transaccion"]),
                limpiar(fila["fecha_creacion"]),
                limpiar(fila["tipo_transaccion"]),
                limpiar(fila["subtipo_transaccion"]),
                float(fila["monto"]),
                int(fila["id_cliente"]),
                limpiar(fila["descripcion"]),
                limpiar(fila["referencia_original"]),
                limpiar(fila["saldo_afectado"]),
                limpiar(fila["estado_deuda"]),
                limpiar(fila["id_empleado"])
            ))


