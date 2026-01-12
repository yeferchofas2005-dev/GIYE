import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class panel_administrador_estadisticas(tk.Frame):

    COLOR_FONDO = "#0a3d62"
    COLOR_CARD = "#ffffff"
    COLOR_TITULO = "#1e293b"
    COLOR_BORDE = "#cbd5e1"
    ANCHO_MAXIMO = 1350

    def __init__(
        self,
        master,
        clientes_mayor_deuda,
        deuda_vs_abono,
        deudas_antiguas,
        transacciones_por_mes,
        on_regresar
    ):
        super().__init__(master, bg=self.COLOR_FONDO)
        self.on_regresar = on_regresar

        self._configurar_estilos()

        # ======================================================
        # BARRA SUPERIOR
        # ======================================================
        barra = tk.Frame(self, bg=self.COLOR_FONDO)
        barra.pack(fill="x", padx=30, pady=(18, 8))

        tk.Button(
            barra,
            text="⬅ Regresar",
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            command=self.on_regresar
        ).pack(side="left", ipadx=12, ipady=6)

        tk.Label(
            barra,
            text="📊 Estadísticas del Sistema",
            bg=self.COLOR_FONDO,
            fg="white",
            font=("Segoe UI", 22, "bold")
        ).pack(side="left", padx=25)

        # ======================================================
        # CONTENEDOR SCROLLABLE
        # ======================================================
        canvas = tk.Canvas(self, bg=self.COLOR_FONDO, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=canvas.yview,
            style="Blue.Vertical.TScrollbar"
        )
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        wrapper = tk.Frame(canvas, bg=self.COLOR_FONDO)
        canvas.create_window((0, 0), window=wrapper, anchor="n")

        contenido = tk.Frame(wrapper, bg=self.COLOR_FONDO, width=self.ANCHO_MAXIMO)
        contenido.pack(fill="x", expand=True)

        contenido.columnconfigure(0, weight=1)
        contenido.columnconfigure(1, weight=1)

        def _actualizar_scroll(_):
            canvas.configure(scrollregion=canvas.bbox("all"))

        wrapper.bind("<Configure>", _actualizar_scroll)

        # ======================================================
        # SCROLL CON RUEDA DEL MOUSE
        # ======================================================
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)       # Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux

        # ======================================================
        # TARJETAS
        # ======================================================
        self._grafico_barras_clientes(
            contenido, clientes_mayor_deuda
        ).grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self._grafico_pastel(
            contenido, deuda_vs_abono
        ).grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self._grafico_barras_por_mes(
            contenido, transacciones_por_mes
        ).grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)

        self._tabla_deudas_antiguas(
            contenido, deudas_antiguas
        ).grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)

    # ======================================================
    # ESTILOS
    # ======================================================
    def _configurar_estilos(self):
        style = ttk.Style()

        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30)

        # Scrollbar azul
        style.configure(
            "Blue.Vertical.TScrollbar",
            background="#2563eb",
            troughcolor="#0a3d62",
            bordercolor="#0a3d62",
            arrowcolor="white"
        )

    # ======================================================
    # CARDS
    # ======================================================
    def _crear_card(self, parent, titulo):
        card = tk.Frame(
            parent,
            bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_BORDE,
            highlightthickness=1
        )

        tk.Label(
            card,
            text=titulo,
            bg=self.COLOR_CARD,
            fg=self.COLOR_TITULO,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=18, pady=(12, 6))

        cuerpo = tk.Frame(card, bg=self.COLOR_CARD)
        cuerpo.pack(fill="both", expand=True, padx=14, pady=14)

        return card, cuerpo

    # ======================================================
    # GRÁFICOS
    # ======================================================
    def _grafico_barras_clientes(self, parent, datos):
        card, cuerpo = self._crear_card(parent, "Clientes con mayor deuda")

        nombres = [d["cliente"] for d in datos]
        montos = [d["total_deuda"] for d in datos]

        fig = Figure(figsize=(6.2, 3.6))
        ax = fig.add_subplot(111)
        ax.bar(range(len(nombres)), montos, color="#2563eb")
        ax.set_xticks(range(len(nombres)))
        ax.set_xticklabels(nombres, rotation=45, ha="right")
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout(pad=1.2)

        FigureCanvasTkAgg(fig, cuerpo).get_tk_widget().pack(fill="both", expand=True)
        return card

    def _grafico_pastel(self, parent, datos):
        card, cuerpo = self._crear_card(parent, "Deuda vs Abonos")

        fig = Figure(figsize=(5.2, 3.6))
        ax = fig.add_subplot(111)
        ax.pie(
            datos.values(),
            labels=datos.keys(),
            autopct="%1.1f%%",
            colors=["#dc2626", "#16a34a"]
        )
        ax.axis("equal")
        fig.tight_layout(pad=1.2)

        FigureCanvasTkAgg(fig, cuerpo).get_tk_widget().pack(fill="both", expand=True)
        return card

    def _grafico_barras_por_mes(self, parent, datos):
        card, cuerpo = self._crear_card(parent, "Deuda y Abono por Mes")

        meses = [d["mes"] for d in datos]
        deudas = [d["deuda"] for d in datos]
        abonos = [d["abono"] for d in datos]

        fig = Figure(figsize=(10.8, 4))
        ax = fig.add_subplot(111)

        x = range(len(meses))
        ax.bar(x, deudas, width=0.4, label="Deuda", color="#dc2626")
        ax.bar([i + 0.4 for i in x], abonos, width=0.4, label="Abono", color="#16a34a")

        ax.set_xticks([i + 0.2 for i in x])
        ax.set_xticklabels(meses, rotation=45)
        ax.legend()
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout(pad=1.2)

        FigureCanvasTkAgg(fig, cuerpo).get_tk_widget().pack(fill="both", expand=True)
        return card

    # ======================================================
    # TABLA
    # ======================================================
    def _tabla_deudas_antiguas(self, parent, datos):
        card, cuerpo = self._crear_card(parent, "Deudas más antiguas")

        tabla = ttk.Treeview(
            cuerpo,
            columns=("cliente", "fecha", "monto"),
            show="headings"
        )

        tabla.heading("cliente", text="Cliente")
        tabla.heading("fecha", text="Fecha")
        tabla.heading("monto", text="Monto")

        for d in datos:
            tabla.insert("", "end", values=(d["cliente"], d["fecha"], d["monto"]))

        tabla.pack(fill="both", expand=True)
        return card
