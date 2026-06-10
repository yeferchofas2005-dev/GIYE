import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry


class panel_dashboard(tk.Frame):

    def __init__(
            self,
            master,
            datos_tabla,
            total_deuda,
            total_abono,
            total_nequi,
            on_nuevo_abono,
            on_nueva_deuda,
            on_filtrar,
            on_tachar,
            on_regresar
    ):

        super().__init__(master, bg="#0b4fa8")

        self.datos_tabla = datos_tabla
        self.total_deuda = total_deuda
        self.total_abono = total_abono
        self.total_nequi = total_nequi
        self.on_filtrar_callback = on_filtrar
        self.on_tachar = on_tachar
        self.on_regresar = on_regresar

        # ==============================
        # SECCIÓN SUPERIOR (BARRA PRINCIPAL)
        # ==============================

        barra_principal = tk.Frame(self, bg="#0b4fa8")
        barra_principal.pack(fill="x", padx=10, pady=10)

        # ==============================
        # BLOQUE IZQUIERDO (FILTROS)
        # ==============================
        bloque_filtros = tk.Frame(barra_principal, bg="#0b4fa8")
        bloque_filtros.pack(side="left", fill="x", expand=True)

        # Fecha
        self.combo_dia = DateEntry(
            bloque_filtros,
            width=12,
            background="darkblue",
            foreground="white",
            date_pattern="yyyy-mm-dd"
        )
        self.combo_dia.pack(side="left", padx=5)
        self.combo_dia.delete(0, "end")

        # Buscar
        tk.Label(
            bloque_filtros,
            text="Buscar:",
            bg="#0b4fa8",
            fg="white",
            font=("Arial", 12)
        ).pack(side="left", padx=5)

        self.entry_buscar = tk.Entry(bloque_filtros, width=18)
        self.entry_buscar.pack(side="left", padx=5)

        # Ordenar
        tk.Label(
            bloque_filtros,
            text="Ordenar:",
            bg="#0b4fa8",
            fg="white",
            font=("Arial", 12)
        ).pack(side="left", padx=5)

        self.combo_ordenar = ttk.Combobox(
            bloque_filtros,
            values=[
                "",
                "Abono Mayor a Menor",
                "Abono Menor a Mayor",
                "Debe Mayor a Menor",
                "Debe Menor a Mayor"
            ],
            width=18,
            state="readonly"
        )
        self.combo_ordenar.current(0)
        self.combo_ordenar.pack(side="left", padx=5)

        # Estado
        tk.Label(
            bloque_filtros,
            text="Estado:",
            bg="#0b4fa8",
            fg="white",
            font=("Arial", 12)
        ).pack(side="left", padx=5)

        self.combo_estado = ttk.Combobox(
            bloque_filtros,
            values=["", "Tachadas", "Sin tachar"],
            width=12,
            state="readonly"
        )
        self.combo_estado.current(0)
        self.combo_estado.pack(side="left", padx=5)

        # ==============================
        # BLOQUE CENTRO (BUSCAR / LIMPIAR / Regresar)
        # ==============================
        bloque_acciones = tk.Frame(barra_principal, bg="#0b4fa8")
        bloque_acciones.pack(side="left", padx=15)

        self.btn_buscar = tk.Button(
            bloque_acciones,
            text="🔍",
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            width=3,
            command=self.on_filtrar
        )
        self.btn_buscar.pack(side="left", padx=5)

        self.btn_limpiar = tk.Button(
            bloque_acciones,
            text="🧹",
            bg="#f39c12",
            fg="white",
            font=("Arial", 12),
            width=3,
            command=self.limpiar_filtros
        )
        self.btn_limpiar.pack(side="left", padx=5)

        btn_regresar = tk.Button(
            barra_principal,
            text="⬅ Regresar",
            bg="#1f1f1f",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=5,
            command=self.on_regresar
        )
        btn_regresar.pack(side="left", padx=10)

        # ==============================
        # BLOQUE DERECHO (BOTONES GRANDES)
        # ==============================
        bloque_botones = tk.Frame(barra_principal, bg="#0b4fa8")
        bloque_botones.pack(side="right")

        self.btn_abono = tk.Button(
            bloque_botones,
            text="+ Nuevo Abono",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=5,
            command=on_nuevo_abono
        )
        self.btn_abono.pack(side="left", padx=8)

        self.btn_deuda = tk.Button(
            bloque_botones,
            text="+ Nueva Deuda",
            bg="#d64545",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=5,
            command=on_nueva_deuda
        )
        self.btn_deuda.pack(side="left", padx=8)

        # ==============================
        # TABLA CENTRAL
        # ==============================

        tabla_frame = tk.Frame(self)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = ("ID", "Nombre", "Debe", "Abono", "Fecha", "Accion")

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            height=15
        )

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=150, anchor="center")

        self.tabla.pack(fill="both", expand=True)

        self.tabla.tag_configure(
            "deuda",
            background="#ffd6d6"
        )

        self.tabla.tag_configure(
            "abono",
            background="#d6ffd6"
        )

        self.tabla.tag_configure(
            "tachado",
            foreground="gray",
            font=("Arial", 11, "overstrike")
        )

        self.tabla.tag_configure(
            "nequi",
            background="#d8b4fe"  # morado suave estilo Nequi
        )

        # ==============================
        # PARTE INFERIOR (TOTALES)
        # ==============================

        pie = tk.Frame(self, bg="#0b4fa8")
        pie.pack(fill="x", padx=10, pady=5)

        self.lbl_total_deuda = tk.Label(
            pie,
            text="Total Deuda: $0",
            bg="#0b4fa8",
            fg="white",
            font=("Arial", 14, "bold")
        )
        self.lbl_total_deuda.pack(side="left", padx=5)

        self.lbl_total_abono = tk.Label(
            pie,
            text="Total Abono: $0",
            bg="#0b4fa8",
            fg="white",
            font=("Arial", 14, "bold")
        )
        self.lbl_total_abono.pack(side="left", padx=30)

        self.lbl_total_nequi = tk.Label(
            pie,
            text="Total Nequi: $0",
            bg="#0b4fa8",
            fg="#d8b4fe",
            font=("Arial", 14, "bold")
        )
        self.lbl_total_nequi.pack(side="right", padx=10)

        self.tabla.column("ID", width=70, anchor="center")

        self.tabla.bind("<ButtonRelease-1>", self._on_row_click)
        
        self.cargar_tabla()

    # ==============================
    # CARGAR TABLA
    # ==============================
    def cargar_tabla(self):

        # limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        # Asegurarse de tener el tag para filas tachadas (gris + overstrike)
        try:
            self.tabla.tag_configure("tachado", foreground="gray", font=("TkDefaultFont", 10, "overstrike"))
        except Exception:
            # en caso de que la plataforma no acepte overstrike directamente, al menos coloreamos
            self.tabla.tag_configure("tachado", foreground="gray")

        # Iterar filas recibidas (acepta tuplas de 6 o 7 elementos)
        for fila in self.datos_tabla:

            # soportar ambos formatos: (id,nombre,debe,abono,fecha,accion)  o
            # (id,nombre,debe,abono,fecha,accion,estado_deuda)
            estado = None
            if len(fila) == 8:
                (
                    id_transaccion,
                    nombre,
                    debe,
                    abono,
                    fecha,
                    accion,
                    estado,
                    subtipo
                ) = fila

                valores_insert = fila
            elif len(fila) == 7:

                (
                    id_transaccion,
                    nombre,
                    debe,
                    abono,
                    fecha,
                    accion,
                    estado
                ) = fila

                subtipo = None
                valores_insert = fila
            else:
                id_transaccion, nombre, debe, abono, fecha, accion = fila
                valores_insert = fila

            # convertirDebe/Abono a número para evaluar (si vienen como string)
            try:
                debe_val = float(debe)
            except Exception:
                debe_val = 0
            try:
                abono_val = float(abono)
            except Exception:
                abono_val = 0

            # determinar tag base por tipo (deuda/abono)
            if estado == "CANCELADA":
                tag = "tachado"

            elif subtipo == "NEQUI_PENDIENTE":
                tag = "nequi"

            elif debe_val > 0:
                tag = "deuda"

            elif abono_val > 0:
                tag = "abono"

            else:
                tag = ""

            # insertar la fila con el/los tags correspondientes
            if tag:
                self.tabla.insert("", "end", values=valores_insert, tags=(tag,))
            else:
                self.tabla.insert("", "end", values=valores_insert)

        # actualizar totales en la UI
        self.lbl_total_deuda.config(text=f"Total Deuda: ${self.total_deuda}")
        self.lbl_total_abono.config(text=f"Total Caja: ${self.total_abono}")
        self.lbl_total_nequi.config(text=f"Total Nequi: ${self.total_nequi}")


    # ==============================
    # APLICAR FILTROS
    # ==============================
    def on_filtrar(self):

        filtros = {
            "fecha": self.combo_dia.get().strip(),
            "nombre": self.entry_buscar.get().strip(),
            "orden": self.combo_ordenar.get().strip(),
            "estado": self.combo_estado.get().strip()
        }

        if self.on_filtrar_callback:
            self.on_filtrar_callback(filtros)

    # ==============================
    # LIMPIAR FILTROS
    # ==============================
    def limpiar_filtros(self):

        self.combo_dia.delete(0, "end")
        self.entry_buscar.delete(0, "end")
        self.combo_ordenar.current(0)
        self.combo_estado.current(0)

        if self.on_filtrar_callback:
            self.on_filtrar_callback({
                "fecha": "",
                "nombre": "",
                "orden": "",
                "estado": ""
            })
    
    # ==============================
    # Click dentro de una fila
    # =============================
    def _on_row_click(self, event):
        item = self.tabla.focus()
        if not item:
            return
        valores = self.tabla.item(item, "values")
        
        #Definimos que si el click es en la columna 6
        columna = self.tabla.identify_column(event.x)
        
        if columna == "#6":
            if valores[5] == "Tachar":
               self.on_tachar(valores[0])

        # Valores = (ID, NombreCliente, Debe, Abono, Fecha, "Ver")
        if self.master.on_click_transaccion:

            id_transaccion = valores[0]

            fila_completa = next(
                (
                    fila
                    for fila in self.datos_tabla
                    if str(fila[0]) == str(id_transaccion)
                ),
                None
            )

            if fila_completa:
                self.master.on_click_transaccion(fila_completa)