# datos_configuracion.py
import hashlib
from .conexion import conexion_bd

class DatosConfiguracion:

    @staticmethod
    def cambiar_contraseña(contraseña):
        db = conexion_bd()

        # Generar hash SHA-256
        hash_contra = hashlib.sha256(contraseña.encode()).hexdigest()

        query = "UPDATE datos_configuracion SET valor = %s WHERE nombre_config = 'clave_admin'"
        db.ejecutar(query, (hash_contra,))


    @staticmethod
    def comparar_contraseña(contraseña):
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
