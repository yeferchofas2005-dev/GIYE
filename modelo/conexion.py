import mysql.connector


class conexion_bd:
    """
    Clase de conexión y ejecución de operaciones
    sobre la base de datos MySQL.
    """

    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = '1074129082'
        self.database = 'ybook'
        self.conn = None
        self.cursor = None

    # ============================
    # CONEXIÓN
    # ============================

    def conectar(self):
        """Abre la conexión con la base de datos."""
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def cerrar(self):
        """Cierra cursor y conexión."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    # ============================
    # CONSULTAS SELECT
    # ============================

    def consultar(self, query, params=None):
        """
        Ejecuta una consulta SELECT.

        Args:
            query (str): Consulta SQL
            params (tuple): Parámetros

        Returns:
            list[dict]: Resultados
        """
        try:
            self.conectar()
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        finally:
            self.cerrar()

    # ============================
    # INSERT / UPDATE / DELETE
    # ============================

    def ejecutar(self, query, params=None):
        """
        Ejecuta una consulta INSERT, UPDATE o DELETE.

        Args:
            query (str): Consulta SQL
            params (tuple): Parámetros
        """
        try:
            self.conectar()
            self.cursor.execute(query, params or ())
            self.conn.commit()
        finally:
            self.cerrar()
