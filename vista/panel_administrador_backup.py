import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry


class panel_administrador_backup(tk.Frame):
    """
    Panel de administración de Backups del sistema.
    """

    def __init__(
        self,
        master,
        correo_backup,
        on_cambiar_correo,
        on_generar_backup,
        on_regresar
    ):
        """
        Constructor del panel.

        Args:
            master (tk.Widget): Contenedor padre
            correo_backup (str): Correo destino actual de los backups
            on_cambiar_correo (callable): Callback para cambiar correo
            on_generar_backup (callable): Callback para generar backup
            on_regresar (callable): Callback para volver al panel anterior
        """
        super().__init__(master, bg="#0b4fa8")

        # ==============================
        # CALLBACKS DEL CONTROLADOR
        # ==============================
        self.on_cambiar_correo = on_cambiar_correo
        self.on_generar_backup = on_generar_backup
        self.on_regresar = on_regresar

        # ==============================
        # BARRA SUPERIOR
        # ==============================
        barra = tk.Frame(self, bg="#0b4fa8")
        barra.pack(fill="x", padx=10, pady=10)

        tk.Label(
            barra,
            text="📦 Gestión de Backups",
            bg="#0b4fa8",
            fg="white",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        tk.Button(
            barra,
            text="⬅ Regresar",
            bg="#1f1f1f",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.on_regresar
        ).pack(side="right")

        # ==============================
        # CONTENIDO PRINCIPAL
        # ==============================
        contenido = tk.Frame(self, bg="white")
        contenido.pack(fill="both", expand=True, padx=20, pady=20)

        # ==============================
        # SECCIÓN: CORREO BACKUP
        # ==============================
        frame_correo = tk.LabelFrame(
            contenido,
            text="📧 Correo destino de backups",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15
        )
        frame_correo.pack(fill="x", pady=10)

        self.var_correo = tk.StringVar(value=correo_backup)

        entry_correo = tk.Entry(
            frame_correo,
            textvariable=self.var_correo,
            font=("Arial", 12),
            state="readonly",
            width=40
        )
        entry_correo.pack(side="left", padx=10)

        tk.Button(
            frame_correo,
            text="✏ Cambiar correo",
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.on_cambiar_correo
        ).pack(side="left", padx=10)

        # ==============================
        # SECCIÓN: RANGO DE FECHAS
        # ==============================
        frame_fechas = tk.LabelFrame(
            contenido,
            text="📅 Rango de fechas del backup",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=15
        )
        frame_fechas.pack(fill="x", pady=10)

        tk.Label(
            frame_fechas,
            text="Fecha inicio:",
            font=("Arial", 11)
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.fecha_inicio = DateEntry(
            frame_fechas,
            width=15,
            date_pattern="yyyy-mm-dd"
        )
        self.fecha_inicio.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(
            frame_fechas,
            text="Fecha fin:",
            font=("Arial", 11)
        ).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.fecha_fin = DateEntry(
            frame_fechas,
            width=15,
            date_pattern="yyyy-mm-dd"
        )
        self.fecha_fin.grid(row=0, column=3, padx=10, pady=5)

        # ==============================
        # SECCIÓN: ACCIONES
        # ==============================
        acciones = tk.Frame(contenido, bg="white")
        acciones.pack(pady=30)

        tk.Button(
            acciones,
            text="📤 Generar y Enviar Backup",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 13, "bold"),
            width=30,
            command=self._generar_backup
        ).pack()

    # ==============================
    # EVENTOS (SOLO LLAMAN AL CONTROLADOR)
    # ==============================
    def _generar_backup(self):
        """
        Solicita al controlador generar el backup
        con las fechas seleccionadas.
        """
        fecha_inicio = self.fecha_inicio.get_date()
        fecha_fin = self.fecha_fin.get_date()

        self.on_generar_backup(fecha_inicio, fecha_fin)
