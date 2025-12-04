import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailSender:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def enviar_mensaje(self, correo_destino, mensaje, asunto="Mensaje desde Yalejo"):
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = correo_destino
        msg['Subject'] = asunto
        msg.attach(MIMEText(mensaje, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False