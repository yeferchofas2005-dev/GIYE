import tkinter as tk
from tkinter import ttk


class panel_administrador(tk.Frame):
    """
    Panel de Administración del sistema.

    Este panel permite al administrador acceder a las funciones
    administrativas principales del sistema:

    - Gestión de empleados
    - Creación y restauración de backups
    - Importación de datos desde Excel
    - Cambio de contraseña de administrador
    - Visualización de estadísticas

    Este panel NO contiene lógica de negocio.
    Todas las acciones se delegan al controlador mediante callbacks.
    """

    def __init__(
        self,
        master,
        on_regresar,
        on_empleados,
        on_backup,
        on_importar_excel,
        on_cambiar_contraseña,
        on_estadisticas
    ):
        super().__init__(master, bg="#0b4fa8")

        self.on_regresar = on_regresar
        self.on_empleados = on_empleados
        self.on_backup = on_backup
        self.on_importar_excel = on_importar_excel
        self.on_cambiar_contraseña = on_cambiar_contraseña
        self.on_estadisticas = on_estadisticas

        # ======================================================
        # BARRA SUPERIOR
        # ======================================================
        barra_superior = tk.Frame(self, bg="#0b4fa8")
        barra_superior.pack(fill="x", padx=10, pady=10)

        btn_regresar = tk.Button(
            barra_superior,
            text="⬅ Regresar",
            bg="#1f1f1f",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=5,
            command=self.on_regresar
        )
        btn_regresar.pack(side="left")

        titulo = tk.Label(
            barra_superior,
            text="Panel de Administración",
            bg="#0b4fa8",
            fg="white",
            font=("Arial", 18, "bold")
        )
        titulo.pack(side="left", padx=20)

        # ======================================================
        # CONTENIDO PRINCIPAL
        # ======================================================
        contenedor = tk.Frame(self, bg="#0b4fa8")
        contenedor.pack(fill="both", expand=True, padx=20, pady=20)

        # ======================================================
        # SECCIÓN BOTONES ADMIN
        # ======================================================
        grid_botones = tk.Frame(contenedor, bg="#0b4fa8")
        grid_botones.pack(expand=True)

        # Configuración de columnas
        for i in range(2):
            grid_botones.columnconfigure(i, weight=1, minsize=280)

        # ---------------- BOTONES ----------------

        self._crear_boton(
            grid_botones,
            fila=0,
            columna=0,
            texto="👤 Gestión de Empleados",
            color="#3498db",
            comando=self.on_empleados
        )

        self._crear_boton(
            grid_botones,
            fila=0,
            columna=1,
            texto="💾 Backup del Sistema",
            color="#2ecc71",
            comando=self.on_backup
        )

        self._crear_boton(
            grid_botones,
            fila=1,
            columna=0,
            texto="📥 Importar desde Excel",
            color="#f39c12",
            comando=self.on_importar_excel
        )

        self._crear_boton(
            grid_botones,
            fila=1,
            columna=1,
            texto="🔐 Cambiar Contraseña Admin",
            color="#d35400",
            comando=self.on_cambiar_contraseña
        )

        self._crear_boton(
            grid_botones,
            fila=2,
            columna=0,
            texto="📊 Estadísticas",
            color="#9b59b6",
            comando=self.on_estadisticas,
            colspan=2
        )

    # ======================================================
    # MÉTODO AUXILIAR PARA BOTONES GRANDES
    # ======================================================
    def _crear_boton(self, parent, fila, columna, texto, color, comando, colspan=1):
        """
        Crea un botón grande de administración con estilo uniforme.

        Args:
            parent (Frame): contenedor donde se agrega
            fila (int): fila del grid
            columna (int): columna del grid
            texto (str): texto del botón
            color (str): color de fondo
            comando (callable): callback al presionar
            colspan (int): número de columnas que ocupa
        """
        boton = tk.Button(
            parent,
            text=texto,
            bg=color,
            fg="white",
            font=("Arial", 14, "bold"),
            width=30,
            height=2,
            command=comando
        )
        boton.grid(
            row=fila,
            column=columna,
            columnspan=colspan,
            padx=15,
            pady=15,
            sticky="nsew"
        )
