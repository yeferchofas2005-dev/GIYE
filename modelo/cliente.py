# cliente.py
"""
Modelo Cliente

Este módulo contiene la clase Cliente, que representa la tabla `clientes`
de la base de datos `ybook`.

Responsabilidades:
- Insertar clientes y empleados
- Consultar clientes
- Validar si un cliente es empleado
- Actualizar información de empleados

Este modelo NO maneja interfaz gráfica ni lógica de negocio.
"""

from .conexion import conexion_bd


class Cliente:
    """
    Modelo de acceso a datos para la tabla `clientes`.
    Todos los métodos son estáticos porque no se maneja estado interno.
    """

    # ============================
    # CREAR
    # ============================

    @staticmethod
    def agregar(nombre, telefono=None, notas=None, empleado=False):
        """
        Inserta un nuevo cliente en la base de datos.

        Args:
            nombre (str): Nombre del cliente
            telefono (str | None): Teléfono del cliente
            notas (str | None): Notas o dirección
            empleado (bool): Indica si el cliente es empleado

        Returns:
            None
        """
        db = conexion_bd()
        query = "INSERT INTO clientes (nombre, telefono, notas, empleado) VALUES (%s, %s, %s, %s)"
        db.ejecutar(query, (nombre, telefono, notas, empleado))

    # ============================
    # CONSULTAS
    # ============================

    @staticmethod
    def buscar_por_nombre(nombre):
        """
        Busca clientes cuyo nombre coincida parcialmente.

        Args:
            nombre (str): Texto a buscar

        Returns:
            list[dict]: Lista de clientes encontrados
        """
        db = conexion_bd()
        query = "SELECT * FROM clientes WHERE nombre LIKE %s"
        return db.consultar(query, (f"%{nombre}%",))

    @staticmethod
    def obtener_por_id(id_cliente):
        """
        Obtiene un cliente por su ID.

        Args:
            id_cliente (int): ID del cliente

        Returns:
            dict | None: Cliente encontrado o None si no existe
        """
        db = conexion_bd()
        query = "SELECT * FROM clientes WHERE id_cliente = %s"
        resultados = db.consultar(query, (id_cliente,))
        return resultados[0] if resultados else None

    @staticmethod
    def obtener_nombre_por_id(id_cliente):
        """
        Obtiene únicamente el nombre de un cliente por su ID.

        Args:
            id_cliente (int): ID del cliente

        Returns:
            str | None: Nombre del cliente o None si no existe
        """
        db = conexion_bd()
        query = "SELECT nombre FROM clientes WHERE id_cliente = %s"
        resultados = db.consultar(query, (id_cliente,))
        return resultados[0]["nombre"] if resultados else None

    @staticmethod
    def obtener_todos():
        """
        Obtiene todos los clientes registrados.

        Returns:
            list[dict]: Lista completa de clientes
        """
        db = conexion_bd()
        query = "SELECT * FROM clientes"
        return db.consultar(query)

    @staticmethod
    def obtener_empleados():
        """
        Obtiene todos los clientes marcados como empleados.

        Returns:
            list[dict]: Lista de empleados
        """
        db = conexion_bd()
        query = "SELECT id_cliente, nombre, telefono, notas FROM clientes WHERE empleado = 1"
        return db.consultar(query)

    # ============================
    # VALIDACIONES
    # ============================

    @staticmethod
    def es_empleado(id_cliente):
        """
        Verifica si un cliente es empleado.

        Args:
            id_cliente (int): ID del cliente

        Returns:
            bool: True si es empleado, False en caso contrario
        """
        db = conexion_bd()
        query = "SELECT empleado FROM clientes WHERE id_cliente = %s"
        resultado = db.consultar(query, (id_cliente,))

        if not resultado:
            return False

        return bool(resultado[0]["empleado"])

    # ============================
    # ACTUALIZAR
    # ============================

    @staticmethod
    def actualizar_empleado(id_cliente, nombre, telefono, notas):
        """
        Actualiza los datos de un empleado existente.

        Solo permite la actualización si el cliente
        está marcado como empleado.

        Args:
            id_cliente (int): ID del empleado
            nombre (str): Nuevo nombre
            telefono (str): Nuevo teléfono
            notas (str): Nuevas notas

        Returns:
            bool: True si la actualización fue ejecutada
        """
        db = conexion_bd()
        query = "UPDATE clientes SET nombre = %s, telefono = %s, notas = %s WHERE id_cliente = %s AND empleado = 1"
        db.ejecutar(query, (nombre, telefono, notas, id_cliente))
        return True
    # ============================
    # ELIMINAR
    # ============================

    @staticmethod
    def eliminar_empleado(id_cliente):
        """
        Elimina un empleado del sistema.

        En realidad, no elimina el registro de la tabla `clientes`,
        sino que cambia el campo `empleado` a FALSE (0).

        Esto se hace porque:
        - Un empleado es también un cliente
        - El historial de transacciones no debe perderse

        Args:
            id_cliente (int): ID del empleado a eliminar

        Returns:
            bool: True si la operación fue ejecutada
        """
        db = conexion_bd()
        query = "UPDATE clientes SET empleado = 0 WHERE id_cliente = %s AND empleado = 1"
        db.ejecutar(query, (id_cliente,))
        return True
