import tkinter as tk
from tkinter import ttk


class panel_inicio(tk.Frame):

    def __init__(self, master=None, on_admin=None, on_empleado=None):
        super().__init__(master, bg="#0b4fa8")  # Fondo azul Yalejo

        # El panel debe aceptar Callbacks.
        self.on_admin = on_admin
        self.on_empleado = on_empleado

        # === CONTENEDOR CENTRAL ===
        centro = tk.Frame(self, bg="#0b4fa8")
        centro.place(relx=0.5, rely=0.5, anchor="center")  # Centrado absoluto

        # --- TÍTULO ---
        titulo = tk.Label(
            centro,
            text="GYIE\nGestión Yalejo de Ingresos y Egresos",
            font=("Arial", 32, "bold"),
            fg="white",
            bg="#0b4fa8",
            justify="center"
        )
        titulo.pack(pady=30)

        # --- BOTÓN ADMIN ---
        self.btn_admin = tk.Button(
            centro,
            text="Entrar como Administrador",
            font=("Arial", 18),
            bg="#1b6fc2",
            fg="white",
            width=25,
            height=2,
            relief="groove",
            command=self._admin_click
        )
        self.btn_admin.pack(pady=10)

        # --- BOTÓN EMPLEADO ---
        self.btn_empleado = tk.Button(
            centro,
            text="Entrar como Empleado",
            font=("Arial", 18),
            bg="#145a9e",
            fg="white",
            width=25,
            height=2,
            relief="groove",
            command=self._empleado_click
        )
        self.btn_empleado.pack(pady=10)

    # Handlers internos
    def _admin_click(self):
        if self.on_admin:
            self.on_admin()

    def _empleado_click(self):
        if self.on_empleado:
            self.on_empleado()
