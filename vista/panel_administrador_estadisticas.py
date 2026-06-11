import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class panel_administrador_estadisticas(tk.Frame):

    # ── Paleta ──────────────────────────────────────────────
    BG           = "#0f172a"
    SIDEBAR      = "#1e293b"
    CARD         = "#1e293b"
    CARD_BORDER  = "#334155"
    ACCENT_BLUE  = "#3b82f6"
    ACCENT_GREEN = "#22c55e"
    ACCENT_RED   = "#ef4444"
    ACCENT_PURP  = "#a855f7"
    ACCENT_AMBER = "#f59e0b"
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_MUTED   = "#94a3b8"
    PLOT_BG      = "#1e293b"
    PLOT_TEXT    = "#94a3b8"

    def __init__(
        self,
        master,
        clientes_mayor_deuda,
        deuda_vs_abono,
        deudas_antiguas,
        transacciones_por_mes,
        resumen_hoy,
        rendimiento_empleados,
        flujo_semanal,
        clientes_riesgosos,
        on_regresar
    ):
        super().__init__(master, bg=self.BG)
        self.on_regresar = on_regresar

        self._configurar_estilos()

        # ══════════════════════════════════════════════════
        # BARRA SUPERIOR
        # ══════════════════════════════════════════════════
        barra = tk.Frame(self, bg=self.SIDEBAR, height=60)
        barra.pack(fill="x")
        barra.pack_propagate(False)

        tk.Button(
            barra,
            text="⬅  Regresar",
            bg=self.BG,
            fg=self.TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            activebackground="#334155",
            activeforeground="white",
            command=self.on_regresar
        ).pack(side="left", padx=20, pady=12, ipadx=12, ipady=4)

        tk.Label(
            barra,
            text="Estadísticas del negocio",
            bg=self.SIDEBAR,
            fg=self.TEXT_PRIMARY,
            font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=10)

        # ══════════════════════════════════════════════════
        # CANVAS SCROLLABLE PRINCIPAL
        # ══════════════════════════════════════════════════
        outer = tk.Frame(self, bg=self.BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=self.BG, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=canvas.yview,
            style="Dark.Vertical.TScrollbar"
        )
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        contenido = tk.Frame(canvas, bg=self.BG)
        win_id = canvas.create_window((0, 0), window=contenido, anchor="nw")

        def _resize(event):
            canvas.itemconfig(win_id, width=event.width)

        def _scroll_update(_):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _resize)
        contenido.bind("<Configure>", _scroll_update)

        self._scroll_canvas = canvas

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        canvas.bind_all("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",   lambda e: canvas.yview_scroll(1, "units"))

        # ══════════════════════════════════════════════════
        # SECCIÓN 1 — RESUMEN DE HOY
        # ══════════════════════════════════════════════════
        self._seccion_titulo(contenido, "📅  Resumen de hoy")

        kpi_hoy = tk.Frame(contenido, bg=self.BG)
        kpi_hoy.pack(fill="x", padx=24, pady=(0, 16))

        self._kpi(kpi_hoy, "Caja hoy",        f"${resumen_hoy['total_caja']:,.0f}",       self.ACCENT_GREEN, "💵")
        self._kpi(kpi_hoy, "Nequi hoy",        f"${resumen_hoy['total_nequi']:,.0f}",      self.ACCENT_PURP,  "📱")
        self._kpi(kpi_hoy, "Deudas nuevas",    f"{resumen_hoy['deudas_nuevas']}",          self.ACCENT_RED,   "📋")
        self._kpi(kpi_hoy, "Monto fiado hoy",  f"${resumen_hoy['monto_deudas_hoy']:,.0f}", self.ACCENT_AMBER, "💸")
        self._kpi(kpi_hoy, "Deudas pagadas",   f"{resumen_hoy['deudas_pagadas']}",         self.ACCENT_BLUE,  "✅")

        # ══════════════════════════════════════════════════
        # SECCIÓN 2 — KPIs GLOBALES
        # ══════════════════════════════════════════════════
        self._seccion_titulo(contenido, "📊  Resumen global")

        kpi_global = tk.Frame(contenido, bg=self.BG)
        kpi_global.pack(fill="x", padx=24, pady=(0, 16))

        total_deuda   = deuda_vs_abono.get("DEUDA", 0)
        total_ingreso = deuda_vs_abono.get("INGRESO", 0)
        ratio         = (total_ingreso / total_deuda * 100) if total_deuda > 0 else 0
        n_morosos     = len(clientes_mayor_deuda)
        n_riesgosos   = len(clientes_riesgosos)

        self._kpi(kpi_global, "Total en deuda",     f"${total_deuda:,.0f}",   self.ACCENT_RED,   "💸")
        self._kpi(kpi_global, "Total recuperado",   f"${total_ingreso:,.0f}", self.ACCENT_GREEN, "✅")
        self._kpi(kpi_global, "Ratio de cobro",     f"{ratio:.1f}%",          self.ACCENT_BLUE,  "📈")
        self._kpi(kpi_global, "Clientes con deuda", f"{n_morosos}",           self.ACCENT_PURP,  "👥")
        self._kpi(kpi_global, "Clientes riesgosos", f"{n_riesgosos}",         self.ACCENT_AMBER, "⚠️")

        # ══════════════════════════════════════════════════
        # SECCIÓN 3 — FLUJO SEMANAL + PASTEL
        # ══════════════════════════════════════════════════
        self._seccion_titulo(contenido, "📆  Flujo de la semana")

        fila_semana = tk.Frame(contenido, bg=self.BG)
        fila_semana.pack(fill="x", padx=24, pady=(0, 16))
        fila_semana.columnconfigure(0, weight=3)
        fila_semana.columnconfigure(1, weight=2)

        self._grafico_flujo_semanal(fila_semana, flujo_semanal).grid(
            row=0, column=0, sticky="nsew", padx=(0, 10)
        )
        self._grafico_pastel(fila_semana, deuda_vs_abono).grid(
            row=0, column=1, sticky="nsew"
        )

        # ══════════════════════════════════════════════════
        # SECCIÓN 4 — CLIENTES CON MAYOR DEUDA + RIESGOSOS
        # ══════════════════════════════════════════════════
        self._seccion_titulo(contenido, "👥  Clientes")

        fila_clientes = tk.Frame(contenido, bg=self.BG)
        fila_clientes.pack(fill="x", padx=24, pady=(0, 16))
        fila_clientes.columnconfigure(0, weight=1)
        fila_clientes.columnconfigure(1, weight=1)

        self._grafico_barras_clientes(fila_clientes, clientes_mayor_deuda).grid(
            row=0, column=0, sticky="nsew", padx=(0, 10)
        )
        self._tabla_clientes_riesgosos(fila_clientes, clientes_riesgosos).grid(
            row=0, column=1, sticky="nsew"
        )

        # ══════════════════════════════════════════════════
        # SECCIÓN 5 — RENDIMIENTO EMPLEADOS
        # ══════════════════════════════════════════════════
        self._seccion_titulo(contenido, "👨‍💼  Rendimiento por empleado")

        fila_empleados = tk.Frame(contenido, bg=self.BG)
        fila_empleados.pack(fill="x", padx=24, pady=(0, 16))

        self._tabla_rendimiento_empleados(fila_empleados, rendimiento_empleados).pack(fill="x")

        # ══════════════════════════════════════════════════
        # SECCIÓN 6 — MOVIMIENTOS POR MES
        # ══════════════════════════════════════════════════
        self._seccion_titulo(contenido, "📅  Movimientos por mes")

        fila_mes = tk.Frame(contenido, bg=self.BG)
        fila_mes.pack(fill="x", padx=24, pady=(0, 16))

        self._grafico_barras_por_mes(fila_mes, transacciones_por_mes).pack(fill="x")

        # ══════════════════════════════════════════════════
        # SECCIÓN 7 — DEUDAS MÁS ANTIGUAS
        # ══════════════════════════════════════════════════
        self._seccion_titulo(contenido, "🕰️  Deudas más antiguas sin pagar")

        fila_antiguas = tk.Frame(contenido, bg=self.BG)
        fila_antiguas.pack(fill="x", padx=24, pady=(0, 32))

        self._tabla_deudas_antiguas(fila_antiguas, deudas_antiguas).pack(fill="x")

    # ══════════════════════════════════════════════════════
    # ESTILOS TTK
    # ══════════════════════════════════════════════════════
    def _configurar_estilos(self):
        style = ttk.Style()

        style.configure(
            "Dark.Vertical.TScrollbar",
            background=self.ACCENT_BLUE,
            troughcolor=self.BG,
            bordercolor=self.BG,
            arrowcolor=self.TEXT_PRIMARY
        )
        style.configure(
            "Dark.Treeview",
            background=self.CARD,
            foreground=self.TEXT_PRIMARY,
            fieldbackground=self.CARD,
            borderwidth=0,
            font=("Segoe UI", 10),
            rowheight=32
        )
        style.configure(
            "Dark.Treeview.Heading",
            background="#334155",
            foreground=self.TEXT_MUTED,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        style.map("Dark.Treeview", background=[("selected", "#3b82f6")])
        style.configure(
            "Thin.Vertical.TScrollbar",
            background="#334155",
            troughcolor=self.CARD,
            bordercolor=self.CARD,
            arrowcolor=self.CARD,
            width=6
        )
        style.configure(
            "Thin.Horizontal.TScrollbar",
            background="#334155",
            troughcolor=self.CARD,
            bordercolor=self.CARD,
            arrowcolor=self.CARD,
            width=6
        )

    # ══════════════════════════════════════════════════════
    # TÍTULO DE SECCIÓN
    # ══════════════════════════════════════════════════════
    def _seccion_titulo(self, parent, texto):
        """Separador visual con línea y acento azul entre secciones."""
        row = tk.Frame(parent, bg=self.BG)
        row.pack(fill="x", padx=24, pady=(20, 8))

        tk.Frame(row, bg=self.ACCENT_BLUE, width=4, height=22).pack(side="left")
        tk.Label(
            row,
            text=f"  {texto}",
            bg=self.BG,
            fg=self.TEXT_PRIMARY,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")
        tk.Frame(row, bg=self.CARD_BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=(12, 0), pady=10
        )

    # ══════════════════════════════════════════════════════
    # KPI CARD
    # ══════════════════════════════════════════════════════
    def _kpi(self, parent, label, valor, color, icono):
        card = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.CARD_BORDER,
            highlightthickness=1
        )
        card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Frame(card, bg=color, width=5).pack(side="left", fill="y")

        inner = tk.Frame(card, bg=self.CARD)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        tk.Label(
            inner,
            text=f"{icono}  {label}",
            bg=self.CARD,
            fg=self.TEXT_MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        tk.Label(
            inner,
            text=valor,
            bg=self.CARD,
            fg=color,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(3, 0))

    # ══════════════════════════════════════════════════════
    # CARD CONTENEDOR
    # ══════════════════════════════════════════════════════
    def _card(self, parent, titulo):
        frame = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.CARD_BORDER,
            highlightthickness=1
        )

        header = tk.Frame(frame, bg=self.CARD)
        header.pack(fill="x", padx=18, pady=(14, 0))

        tk.Frame(header, bg=self.ACCENT_BLUE, width=4, height=16).pack(side="left")
        tk.Label(
            header,
            text=f"  {titulo}",
            bg=self.CARD,
            fg=self.TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold")
        ).pack(side="left")

        cuerpo = tk.Frame(frame, bg=self.CARD)
        cuerpo.pack(fill="both", expand=True, padx=14, pady=14)

        return frame, cuerpo

    # ══════════════════════════════════════════════════════
    # HELPER: figura oscura
    # ══════════════════════════════════════════════════════
    def _figura(self, w, h):
        fig = Figure(figsize=(w, h), facecolor=self.PLOT_BG)
        fig.subplots_adjust(left=0.12, right=0.97, top=0.92, bottom=0.22)
        return fig

    def _estilo_ax(self, ax):
        ax.set_facecolor(self.PLOT_BG)
        ax.tick_params(colors=self.PLOT_TEXT, labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for s in ["left", "bottom"]:
            ax.spines[s].set_color("#334155")
        ax.yaxis.label.set_color(self.PLOT_TEXT)
        ax.xaxis.label.set_color(self.PLOT_TEXT)

    # ══════════════════════════════════════════════════════
    # HELPER: embeber figura y reenviar scroll al canvas principal
    # ══════════════════════════════════════════════════════
    def _embed_figura(self, fig, parent):
        widget = FigureCanvasTkAgg(fig, parent).get_tk_widget()
        widget.pack(fill="both", expand=True)
        sc = self._scroll_canvas
        widget.bind("<MouseWheel>", lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))
        widget.bind("<Button-4>",   lambda e: sc.yview_scroll(-1, "units"))
        widget.bind("<Button-5>",   lambda e: sc.yview_scroll(1, "units"))

    # ══════════════════════════════════════════════════════
    # HELPER: tabla oscura reutilizable con scroll interno
    # ══════════════════════════════════════════════════════
    def _tabla(self, parent, columnas, filas, anchos=None, altura=8):
        """
        Crea un Treeview oscuro con scrollbar vertical interna minimalista.

        Parámetros:
        -----------
        columnas : list de tuplas (id, texto_cabecera, anchor)
        filas    : list de tuplas con los valores de cada fila
        anchos   : dict {id: ancho_px} opcional
        altura   : número máximo de filas visibles antes de activar scroll
        """
        contenedor = tk.Frame(parent, bg=self.CARD)
        contenedor.pack(fill="both", expand=True)

        cols = [c[0] for c in columnas]
        tabla = ttk.Treeview(
            contenedor,
            columns=cols,
            show="headings",
            style="Dark.Treeview",
            height=min(len(filas), altura)
        )

        for col_id, col_texto, col_anchor in columnas:
            tabla.heading(col_id, text=col_texto)
            ancho = anchos.get(col_id, 150) if anchos else 150
            tabla.column(col_id, width=ancho, anchor=col_anchor)

        tabla.tag_configure("par",   background="#243044")
        tabla.tag_configure("impar", background=self.CARD)

        for i, fila in enumerate(filas):
            tabla.insert("", "end", values=fila, tags=("par" if i % 2 == 0 else "impar",))

        scroll = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=tabla.yview,
            style="Thin.Vertical.TScrollbar"
        )
        tabla.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)

        return contenedor

    # ══════════════════════════════════════════════════════
    # GRÁFICO: FLUJO SEMANAL (LÍNEA — ÚLTIMOS 7 DÍAS)
    # ══════════════════════════════════════════════════════
    def _grafico_flujo_semanal(self, parent, datos):
        card, cuerpo = self._card(parent, "Entradas vs deudas — últimos 7 días")

        dias     = [d["dia"]     for d in datos]
        ingresos = [d["ingreso"] for d in datos]
        deudas   = [d["deuda"]   for d in datos]

        fig = self._figura(6, 3.6)
        ax  = fig.add_subplot(111)
        self._estilo_ax(ax)

        ax.plot(dias, ingresos, color=self.ACCENT_GREEN, marker="o", linewidth=2, markersize=5, label="Ingresos")
        ax.plot(dias, deudas,   color=self.ACCENT_RED,   marker="o", linewidth=2, markersize=5, label="Deudas")
        ax.fill_between(dias, ingresos, alpha=0.08, color=self.ACCENT_GREEN)
        ax.fill_between(dias, deudas,   alpha=0.08, color=self.ACCENT_RED)

        ax.set_xticklabels(dias, rotation=35, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.15, color="#475569")
        ax.legend(fontsize=9, frameon=False, labelcolor=self.TEXT_MUTED)

        self._embed_figura(fig, cuerpo)
        return card

    # ══════════════════════════════════════════════════════
    # GRÁFICO: PASTEL DEUDA VS INGRESO GLOBAL
    # ══════════════════════════════════════════════════════
    def _grafico_pastel(self, parent, datos):
        card, cuerpo = self._card(parent, "Deuda vs ingresos — global")

        fig = Figure(figsize=(4.2, 3.6), facecolor=self.PLOT_BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(self.PLOT_BG)

        wedges, _, autotexts = ax.pie(
            datos.values(),
            labels=None,
            autopct="%1.1f%%",
            colors=[self.ACCENT_RED, self.ACCENT_GREEN],
            startangle=90,
            wedgeprops={"linewidth": 2, "edgecolor": self.PLOT_BG}
        )
        for at in autotexts:
            at.set_color(self.TEXT_PRIMARY)
            at.set_fontsize(10)

        ax.legend(
            wedges,
            [f"{k}  ${v:,.0f}" for k, v in datos.items()],
            loc="lower center",
            bbox_to_anchor=(0.5, -0.12),
            ncol=1, fontsize=9, frameon=False,
            labelcolor=self.TEXT_MUTED
        )

        fig.tight_layout(pad=1.5)
        self._embed_figura(fig, cuerpo)
        return card

    # ══════════════════════════════════════════════════════
    # GRÁFICO: CLIENTES CON MAYOR DEUDA (BARRAS HORIZONTALES)
    # ══════════════════════════════════════════════════════
    def _grafico_barras_clientes(self, parent, datos):
        card, cuerpo = self._card(parent, "Clientes con mayor deuda pendiente")

        nombres = [d["cliente"]     for d in datos]
        montos  = [d["total_deuda"] for d in datos]

        # alto dinámico: 0.5 pulgadas por cliente, mínimo 3.6
        alto = max(3.6, len(nombres) * 0.52)

        fig = Figure(figsize=(5.5, alto), facecolor=self.PLOT_BG)
        # margen izquierdo amplio para nombres largos
        fig.subplots_adjust(left=0.38, right=0.88, top=0.95, bottom=0.08)
        ax = fig.add_subplot(111)
        self._estilo_ax(ax)

        bars  = ax.barh(nombres, montos, color=self.ACCENT_RED, height=0.55)
        max_m = max(montos) if montos else 1

        for bar, monto in zip(bars, montos):
            ax.text(
                bar.get_width() + max_m * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"${monto:,.0f}",
                va="center", color=self.TEXT_MUTED, fontsize=8
            )

        ax.invert_yaxis()
        ax.set_xlabel("Pesos ($)", color=self.PLOT_TEXT, fontsize=9)
        ax.grid(axis="x", alpha=0.15, color="#475569")

        # contenedor con scroll vertical para cuando hay muchos clientes
        scroll_frame = tk.Frame(cuerpo, bg=self.CARD)
        scroll_frame.pack(fill="both", expand=True)

        v_scroll = ttk.Scrollbar(
            scroll_frame, orient="vertical", style="Thin.Vertical.TScrollbar"
        )
        v_scroll.pack(side="right", fill="y")

        canvas_fig = FigureCanvasTkAgg(fig, scroll_frame)
        widget = canvas_fig.get_tk_widget()
        widget.pack(side="left", fill="both", expand=True)

        v_scroll.configure(command=lambda *a: widget.yview(*a))
        widget.configure(yscrollcommand=v_scroll.set)

        sc = self._scroll_canvas
        widget.bind("<MouseWheel>", lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))
        widget.bind("<Button-4>",   lambda e: sc.yview_scroll(-1, "units"))
        widget.bind("<Button-5>",   lambda e: sc.yview_scroll(1, "units"))

        return card

    # ══════════════════════════════════════════════════════
    # TABLA: CLIENTES RIESGOSOS (sin pagar hace +30 días)
    # ══════════════════════════════════════════════════════
    def _tabla_clientes_riesgosos(self, parent, datos):
        card, cuerpo = self._card(parent, "⚠️  Clientes riesgosos — sin pagar hace +30 días")

        filas = [
            (
                d["cliente"],
                f"{d['dias_sin_pagar']} días",
                f"${d['total_pendiente']:,.0f}",
                d["desde"]
            )
            for d in datos
        ]

        self._tabla(
            cuerpo,
            columnas=[
                ("cliente", "Cliente",        "w"),
                ("dias",    "Sin pagar",       "center"),
                ("monto",   "Monto pendiente", "e"),
                ("desde",   "Desde",           "center"),
            ],
            filas=filas,
            anchos={"cliente": 180, "dias": 90, "monto": 130, "desde": 100}
        )

        return card

    # ══════════════════════════════════════════════════════
    # TABLA: RENDIMIENTO POR EMPLEADO
    # ══════════════════════════════════════════════════════
    def _tabla_rendimiento_empleados(self, parent, datos):
        card, cuerpo = self._card(parent, "Fiado registrado y porcentaje recuperado por empleado")

        filas = [
            (
                d["empleado"],
                f"${d['total_fiado']:,.0f}",
                f"${d['total_recuperado']:,.0f}",
                f"{d['porcentaje']}%"
            )
            for d in datos
        ]

        self._tabla(
            cuerpo,
            columnas=[
                ("empleado",   "Empleado",    "w"),
                ("fiado",      "Total fiado", "e"),
                ("recuperado", "Recuperado",  "e"),
                ("porcentaje", "% cobrado",   "center"),
            ],
            filas=filas,
            anchos={"empleado": 220, "fiado": 160, "recuperado": 160, "porcentaje": 100},
            altura=6
        )

        return card

    # ══════════════════════════════════════════════════════
    # GRÁFICO: MOVIMIENTOS POR MES (BARRAS CON SCROLL HORIZONTAL)
    # ══════════════════════════════════════════════════════
    def _grafico_barras_por_mes(self, parent, datos):
        card, cuerpo = self._card(parent, "Deuda y abono por mes")

        meses  = [d["mes"]   for d in datos]
        deudas = [d["deuda"] for d in datos]
        abonos = [d["abono"] for d in datos]

        ancho = max(11, len(meses) * 0.9)
        fig = self._figura(ancho, 3.6)
        ax  = fig.add_subplot(111)
        self._estilo_ax(ax)

        x = range(len(meses))
        w = 0.38
        ax.bar(x,                deudas, width=w, label="Deuda",   color=self.ACCENT_RED,   alpha=0.9)
        ax.bar([i+w for i in x], abonos, width=w, label="Ingreso", color=self.ACCENT_GREEN, alpha=0.9)

        ax.set_xticks([i + w / 2 for i in x])
        ax.set_xticklabels(meses, rotation=40, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.15, color="#475569")
        ax.legend(fontsize=9, frameon=False, labelcolor=self.TEXT_MUTED)

        scroll_frame = tk.Frame(cuerpo, bg=self.CARD)
        scroll_frame.pack(fill="both", expand=True)

        h_scroll = ttk.Scrollbar(
            scroll_frame, orient="horizontal", style="Thin.Horizontal.TScrollbar"
        )
        h_scroll.pack(side="bottom", fill="x")

        canvas_fig = FigureCanvasTkAgg(fig, scroll_frame)
        widget = canvas_fig.get_tk_widget()
        widget.pack(side="top", fill="both", expand=True)

        h_scroll.configure(command=lambda *a: widget.xview(*a))
        widget.configure(xscrollcommand=h_scroll.set)

        sc = self._scroll_canvas
        widget.bind("<MouseWheel>", lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))
        widget.bind("<Button-4>",   lambda e: sc.yview_scroll(-1, "units"))
        widget.bind("<Button-5>",   lambda e: sc.yview_scroll(1, "units"))

        return card

    # ══════════════════════════════════════════════════════
    # TABLA: DEUDAS MÁS ANTIGUAS (con columna de días)
    # ══════════════════════════════════════════════════════
    def _tabla_deudas_antiguas(self, parent, datos):
        card, cuerpo = self._card(parent, "Deudas más antiguas sin pagar")

        filas = [
            (
                d["cliente"],
                d["fecha"],
                f"{d['dias']} días",
                f"${d['monto']:,.0f}"
            )
            for d in datos
        ]

        self._tabla(
            cuerpo,
            columnas=[
                ("cliente", "Cliente",        "w"),
                ("fecha",   "Desde",          "center"),
                ("dias",    "Días pendiente", "center"),
                ("monto",   "Monto",          "e"),
            ],
            filas=filas,
            anchos={"cliente": 240, "fecha": 130, "dias": 120, "monto": 150}
        )

        return card