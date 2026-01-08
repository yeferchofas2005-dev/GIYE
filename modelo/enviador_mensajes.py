import os
import smtplib
from email.message import EmailMessage

class enviador_mensajes:
    """
    Clase encargada únicamente del envío de correos.
    Las credenciales SMTP se leen desde variables de entorno.
    """

    def enviar_mensaje_html_con_archivos(destinatario: str, asunto: str, mensaje_html: str, rutas_archivos: list):
        """
        Envía un correo HTML con múltiples archivos adjuntos.

        Args:
            destinatario (str): Correo destino
            asunto (str): Asunto del correo
            mensaje_html (str): Cuerpo del mensaje en HTML
            rutas_archivos (list): Lista de rutas de archivos a adjuntar
        """

        stpm_server = os.getenv("SMTP_SERVER")
        stpm_port = int(os.getenv("SMTP_PORT"))
        stpm_user = os.getenv("SMTP_USER")
        stpm_password = os.getenv("SMTP_PASSWORD")
        stpm_use_tls = os.getenv("SMTP_USE_TLS").lower() == 'true'

        if not all([stpm_server, stpm_port, stpm_user, stpm_password]):
            raise ValueError("Faltan credenciales SMTP en las variables de entorno.")

        msg = EmailMessage()
        msg["From"] = stpm_user
        msg["To"] = destinatario
        msg["Subject"] = asunto

        # Contenido HTML
        msg.add_alternative(mensaje_html, subtype="html")

        # Adjuntar múltiples archivos
        for ruta in rutas_archivos:
            if not os.path.exists(ruta):
                continue

            with open(ruta, "rb") as archivo:
                contenido = archivo.read()
                nombre = os.path.basename(ruta)

                msg.add_attachment(
                    contenido,
                    maintype="application",
                    subtype="octet-stream",
                    filename=nombre
                )

        try:
            with smtplib.SMTP(stpm_server, stpm_port) as servidor:
                if stpm_use_tls:
                    servidor.starttls()

                servidor.login(stpm_user, stpm_password)
                servidor.send_message(msg)

        except smtplib.SMTPException as e:
            raise RuntimeError(f"Error al enviar el correo: {e}")
    