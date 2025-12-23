import tkinter as tk
from tkinter import ttk


class panel_administrador_empleado(tk.Frame):
    """
    Panel de administración de empleados.

    RESPONSABILIDAD:
    -----------------
    Esta clase representa ÚNICAMENTE la VISTA (GUI) del módulo
    de gestión de empleados.

    ❌ No accede a la base de datos
    ❌ No mantiene estado interno
    ❌ No actualiza listas
    ❌ No refresca datos por su cuenta

    ✅ Muestra información recibida
    ✅ Dispara eventos al controlador (callbacks)
    """

    def __init__(
        self,
        master,
        empleados,
        on_agregar,
        on_editar,
        on_eliminar,
        on_regresar
    ):
        """
        Constructor del panel.

        Args:
            master (tk.Widget): Contenedor padre
            empleados (list[dict]): Lista de empleados obtenida desde BD
            on_agregar (callable): Callback para agregar empleado
            on_editar (callable): Callback para editar empleado
            on_eliminar (callable): Callback para eliminar empleado
            on_regresar (callable): Callback para volver al menú anterior
        """
        super().__init__(master, bg="#0b4fa8")

        # ==============================
        # CALLBACKS DEL CONTROLADOR
        # ==============================
        self.on_agregar = on_agregar
        self.on_editar = on_editar
        self.on_eliminar = on_eliminar
        self.on_regresar = on_regresar

        # ==============================
        # BARRA SUPERIOR
        # ==============================
        barra = tk.Frame(self, bg="#0b4fa8")
        barra.pack(fill="x", padx=10, pady=10)

        tk.Label(
            barra,
            text="👨‍💼 Gestión de Empleados",
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
        # TABLA DE EMPLEADOS
        # ==============================
        tabla_frame = tk.Frame(self)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columnas = ("ID", "Nombre", "Teléfono", "Notas")

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            height=15
        )

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=200)

        # Columna ID oculta (uso interno)
        self.tabla.column("ID", width=0, stretch=False)

        self.tabla.pack(fill="both", expand=True)

        # ==============================
        # BOTONES CRUD
        # ==============================
        acciones = tk.Frame(self, bg="#0b4fa8")
        acciones.pack(pady=10)

        tk.Button(
            acciones,
            text="➕ Agregar",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            command=self._agregar_empleado
        ).pack(side="left", padx=10)

        tk.Button(
            acciones,
            text="✏ Editar",
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            command=self._editar_seleccionado
        ).pack(side="left", padx=10)

        tk.Button(
            acciones,
            text="🗑 Eliminar",
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12, "bold"),
            width=15,
            command=self._eliminar_seleccionado
        ).pack(side="left", padx=10)

        # ==============================
        # CARGA INICIAL
        # ==============================
        self._mostrar_empleados(empleados)

    # ==============================
    # MOSTRAR EMPLEADOS
    # ==============================
    def _mostrar_empleados(self, empleados):
        """
        Carga los empleados en la tabla.

        Este método SOLO se usa al crear el panel.
        """
        self.tabla.delete(*self.tabla.get_children())

        for emp in empleados:
            self.tabla.insert(
                "",
                "end",
                values=(
                    emp["id_cliente"],
                    emp["nombre"],
                    emp["telefono"],
                    emp["notas"]
                )
            )

    # ==============================
    # OBTENER FILA SELECCIONADA
    # ==============================
    def _obtener_seleccion(self):
        """
        Retorna la fila seleccionada en la tabla.

        Returns:
            tuple | None: Datos seleccionados o None
        """
        item = self.tabla.focus()
        if not item:
            return None
        return self.tabla.item(item, "values")

    # ==============================
    # EVENTOS (SOLO LLAMAN AL CONTROLADOR)
    # ==============================
    def _agregar_empleado(self):
        """
        Solicita al controlador agregar un empleado.
        """
        self.on_agregar()

    def _editar_seleccionado(self):
        """
        Solicita al controlador editar el empleado seleccionado.
        """
        datos = self._obtener_seleccion()
        if not datos:
            return

        self.on_editar(datos)

    def _eliminar_seleccionado(self):
        """
        Solicita al controlador eliminar el empleado seleccionado.
        """
        datos = self._obtener_seleccion()
        if not datos:
            return

        self.on_eliminar(datos)
