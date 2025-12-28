from dotenv import load_dotenv
from controlador.controlador import Controller

load_dotenv()

if __name__ == "__main__":
    app = Controller()
    app.iniciar()