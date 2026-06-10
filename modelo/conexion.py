import pymysql
import os

class conexion_bd:

    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.port = int(os.getenv("DB_PORT", 3306))

    def conectar(self):
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()

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
