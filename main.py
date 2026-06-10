import os
import sys
from dotenv import load_dotenv
from controlador.controlador import Controller

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH, override=True)


if __name__ == "__main__":
    app = Controller()
    app.iniciar()
