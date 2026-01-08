# datos_configuracion.py
import hashlib
from .conexion import conexion_bd


class DatosConfiguracion:
    """
    Clase encargada de gestionar los datos de configuración del sistema
    almacenados en la base de datos.

    RESPONSABILIDAD:
    -----------------
    - Administrar configuraciones críticas del sistema
    - Manejar credenciales administrativas
    - Gestionar parámetros globales como correos de respaldo

    NOTAS:
    ------
    - Todas las operaciones se realizan directamente sobre la tabla
      'datos_configuracion'
    - Los métodos son estáticos ya que no requieren estado de instancia
    """

    @staticmethod
    def cambiar_contraseña(contraseña):
        """
        Actualiza la contraseña del administrador del sistema.

        RESPONSABILIDAD:
        -----------------
        - Recibir una nueva contraseña en texto plano
        - Generar un hash seguro usando SHA-256
        - Almacenar el hash de la contraseña en la base de datos

        PARÁMETROS:
        -----------
        contraseña (str):
            Nueva contraseña del administrador en texto plano

        FLUJO:
        ------
        1. Establece conexión con la base de datos
        2. Genera el hash SHA-256 de la contraseña ingresada
        3. Ejecuta una consulta UPDATE para guardar el hash
        4. Finaliza el proceso sin retornar valores

        NOTAS:
        ------
        - La contraseña nunca se almacena en texto plano
        - El hash SHA-256 garantiza mayor seguridad
        - Solo existe una contraseña administrativa en el sistema
        """
        db = conexion_bd()

        # Generar hash SHA-256
        hash_contra = hashlib.sha256(contraseña.encode()).hexdigest()

        query = "UPDATE datos_configuracion SET valor = %s WHERE nombre_config = 'clave_admin'"
        db.ejecutar(query, (hash_contra,))


    @staticmethod
    def comparar_contraseña(contraseña):
        """
        Verifica si una contraseña ingresada coincide con la almacenada.

        RESPONSABILIDAD:
        -----------------
        - Obtener el hash de la contraseña almacenada
        - Generar el hash de la contraseña ingresada
        - Comparar ambos hashes para validar acceso

        PARÁMETROS:
        -----------
        contraseña (str):
            Contraseña ingresada por el usuario

        FLUJO:
        ------
        1. Establece conexión con la base de datos
        2. Consulta el hash almacenado de la contraseña admin
        3. Genera el hash SHA-256 de la contraseña ingresada
        4. Compara ambos hashes
        5. Retorna el resultado de la comparación

        RETORNA:
        --------
        bool:
            True  -> Si las contraseñas coinciden  
            False -> Si no coinciden o no existe configuración

        NOTAS:
        ------
        - No se compara texto plano, solo hashes
        - Evita exposición de credenciales sensibles
        - Retorna False si no existe contraseña configurada
        """
        db = conexion_bd()

        # Obtener hash almacenado
        query = "SELECT valor FROM datos_configuracion WHERE nombre_config = 'clave_admin'"
        resultados = db.consultar(query)

        if not resultados:
            return False

        hash_guardado = resultados[0]["valor"]

        # Hash de la contraseña ingresada
        hash_ingresado = hashlib.sha256(contraseña.encode()).hexdigest()

        # Comparar hashes
        return hash_guardado == hash_ingresado
    

    @staticmethod
    def obtener_correo_backup():
        """
        Obtiene el correo electrónico configurado para recibir backups.

        RESPONSABILIDAD:
        -----------------
        - Consultar el correo destino de backups desde la base de datos
        - Retornar el valor almacenado para su uso en envíos automáticos

        PARÁMETROS:
        -----------
        Ninguno

        FLUJO:
        ------
        1. Establece conexión con la base de datos
        2. Consulta el valor del correo de backup
        3. Verifica si existe el registro
        4. Retorna el correo configurado

        RETORNA:
        --------
        str | None:
            Correo electrónico configurado o None si no existe

        NOTAS:
        ------
        - Este correo se usa para backups manuales y automáticos
        - Debe ser configurado previamente desde el sistema
        """
        db = conexion_bd()

        query = "SELECT valor FROM datos_configuracion WHERE nombre_config = 'correo_backup_destino'"
        resultados = db.consultar(query)

        if not resultados:
            return None

        return resultados[0]["valor"]


    @staticmethod
    def cambiar_correo_backup(correo):
        """
        Actualiza el correo electrónico de destino para los backups.

        RESPONSABILIDAD:
        -----------------
        - Recibir un nuevo correo electrónico
        - Actualizar el correo de destino en la base de datos
        - Permitir la reconfiguración del sistema de backups

        PARÁMETROS:
        -----------
        correo (str):
            Nuevo correo electrónico para recibir backups

        FLUJO:
        ------
        1. Establece conexión con la base de datos
        2. Ejecuta una consulta UPDATE con el nuevo correo
        3. Guarda el cambio en la configuración del sistema

        NOTAS:
        ------
        - No valida formato del correo (se asume validación previa)
        - El cambio afecta backups futuros inmediatamente
        """
        db = conexion_bd()

        query = "UPDATE datos_configuracion SET valor = %s WHERE nombre_config = 'correo_backup_destino'"
        db.ejecutar(query, (correo,))
