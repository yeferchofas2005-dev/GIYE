import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class panel_administrador_estadisticas(tk.Frame):

    # ── Paleta ──────────────────────────────────────────────
    BG           = "#0f172a"   # fondo principal azul muy oscuro
    SIDEBAR      = "#1e293b"   # barra superior
    CARD         = "#1e293b"   # tarjetas
    CARD_BORDER  = "#334155"   # borde tarjeta
    ACCENT_BLUE  = "#3b82f6"   # azul principal
    ACCENT_GREEN = "#22c55e"   # verde (abonos)
    ACCENT_RED   = "#ef4444"   # rojo (deudas)
    ACCENT_PURP  = "#a855f7"   # morado (nequi)
    TEXT_PRIMARY = "#f1f5f9"   # texto principal
    TEXT_MUTED   = "#94a3b8"   # texto secundario
    PLOT_BG      = "#1e293b"   # fondo de gráficos
    PLOT_TEXT    = "#94a3b8"   # texto de ejes

    def __init__(
        self,
        master,
        clientes_mayor_deuda,
        deuda_vs_abono,
        deudas_antiguas,
        transacciones_por_mes,
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
        # CANVAS SCROLLABLE
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

        # guardamos referencia para usarla en los helpers de gráficos
        self._scroll_canvas = canvas

        def _scroll(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _scroll)
        canvas.bind_all("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",   lambda e: canvas.yview_scroll(1,  "units"))

        # ══════════════════════════════════════════════════
        # FILA 0 — KPI CARDS
        # ══════════════════════════════════════════════════
        kpi_row = tk.Frame(contenido, bg=self.BG)
        kpi_row.pack(fill="x", padx=24, pady=(20, 0))

        total_deuda  = deuda_vs_abono.get("DEUDA", 0)
        total_ingreso = deuda_vs_abono.get("INGRESO", 0)
        ratio = (total_ingreso / total_deuda * 100) if total_deuda > 0 else 0
        n_morosos = len(clientes_mayor_deuda)

        self._kpi(kpi_row, "Total en deuda",    f"${total_deuda:,.0f}",   self.ACCENT_RED,   "💸")
        self._kpi(kpi_row, "Total recuperado",  f"${total_ingreso:,.0f}", self.ACCENT_GREEN, "✅")
        self._kpi(kpi_row, "Ratio de cobro",    f"{ratio:.1f}%",          self.ACCENT_BLUE,  "📈")
        self._kpi(kpi_row, "Clientes con deuda",f"{n_morosos}",           self.ACCENT_PURP,  "👥")

        # ══════════════════════════════════════════════════
        # FILA 1 — BARRAS CLIENTES  +  PASTEL
        # ══════════════════════════════════════════════════
        fila1 = tk.Frame(contenido, bg=self.BG)
        fila1.pack(fill="x", padx=24, pady=16)
        fila1.columnconfigure(0, weight=3)
        fila1.columnconfigure(1, weight=2)

        self._grafico_barras_clientes(fila1, clientes_mayor_deuda).grid(
            row=0, column=0, sticky="nsew", padx=(0, 10)
        )
        self._grafico_pastel(fila1, deuda_vs_abono).grid(
            row=0, column=1, sticky="nsew"
        )

        # ══════════════════════════════════════════════════
        # FILA 2 — BARRAS POR MES
        # ══════════════════════════════════════════════════
        fila2 = tk.Frame(contenido, bg=self.BG)
        fila2.pack(fill="x", padx=24, pady=(0, 16))

        self._grafico_barras_por_mes(fila2, transacciones_por_mes).pack(
            fill="x"
        )

        # ══════════════════════════════════════════════════
        # FILA 3 — TABLA DEUDAS ANTIGUAS
        # ══════════════════════════════════════════════════
        fila3 = tk.Frame(contenido, bg=self.BG)
        fila3.pack(fill="x", padx=24, pady=(0, 24))

        self._tabla_deudas_antiguas(fila3, deudas_antiguas).pack(fill="x")

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

        # scrollbar delgada y discreta para tablas internas
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
    # KPI CARD
    # ══════════════════════════════════════════════════════
    def _kpi(self, parent, label, valor, color, icono):
        card = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.CARD_BORDER,
            highlightthickness=1
        )
        card.pack(side="left", fill="both", expand=True, padx=(0, 12))

        # franja de color izquierda
        tk.Frame(card, bg=color, width=5).pack(side="left", fill="y")

        inner = tk.Frame(card, bg=self.CARD)
        inner.pack(side="left", fill="both", expand=True, padx=16, pady=14)

        tk.Label(
            inner,
            text=f"{icono}  {label}",
            bg=self.CARD,
            fg=self.TEXT_MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        tk.Label(
            inner,
            text=valor,
            bg=self.CARD,
            fg=color,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", pady=(4, 0))

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

        tk.Frame(header, bg=self.ACCENT_BLUE, width=4, height=18).pack(side="left")
        tk.Label(
            header,
            text=f"  {titulo}",
            bg=self.CARD,
            fg=self.TEXT_PRIMARY,
            font=("Segoe UI", 12, "bold")
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

    def _estilo_ax(self, ax, title=""):
        ax.set_facecolor(self.PLOT_BG)
        ax.tick_params(colors=self.PLOT_TEXT, labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for s in ["left", "bottom"]:
            ax.spines[s].set_color("#334155")
        ax.yaxis.label.set_color(self.PLOT_TEXT)
        ax.xaxis.label.set_color(self.PLOT_TEXT)
        if title:
            ax.set_title(title, color=self.TEXT_MUTED, fontsize=9, pad=6)

    # ══════════════════════════════════════════════════════
    # HELPER: embeber figura y reenviar scroll
    # ══════════════════════════════════════════════════════
    def _embed_figura(self, fig, parent):
        widget = FigureCanvasTkAgg(fig, parent).get_tk_widget()
        widget.pack(fill="both", expand=True)
        sc = self._scroll_canvas
        widget.bind("<MouseWheel>", lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))
        widget.bind("<Button-4>",   lambda e: sc.yview_scroll(-1, "units"))
        widget.bind("<Button-5>",   lambda e: sc.yview_scroll(1,  "units"))

    # ══════════════════════════════════════════════════════
    # GRÁFICO: CLIENTES CON MAYOR DEUDA
    # ══════════════════════════════════════════════════════
    def _grafico_barras_clientes(self, parent, datos):
        card, cuerpo = self._card(parent, "Clientes con mayor deuda pendiente")

        nombres = [d["cliente"] for d in datos]
        montos  = [d["total_deuda"] for d in datos]

        fig = self._figura(6, 3.8)
        ax  = fig.add_subplot(111)
        self._estilo_ax(ax)

        bars = ax.barh(nombres, montos, color=self.ACCENT_RED, height=0.55)

        # etiquetas de valor
        for bar, monto in zip(bars, montos):
            ax.text(
                bar.get_width() + max(montos) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"${monto:,.0f}",
                va="center",
                color=self.TEXT_MUTED,
                fontsize=8
            )

        ax.invert_yaxis()
        ax.set_xlabel("Pesos ($)", color=self.PLOT_TEXT, fontsize=9)
        ax.grid(axis="x", alpha=0.15, color="#475569")

        self._embed_figura(fig, cuerpo)
        return card

    # ══════════════════════════════════════════════════════
    # GRÁFICO: PASTEL DEUDA VS ABONO
    # ══════════════════════════════════════════════════════
    def _grafico_pastel(self, parent, datos):
        card, cuerpo = self._card(parent, "Deuda vs ingresos")

        fig = Figure(figsize=(4.2, 3.8), facecolor=self.PLOT_BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(self.PLOT_BG)

        colores = [self.ACCENT_RED, self.ACCENT_GREEN]
        wedges, texts, autotexts = ax.pie(
            datos.values(),
            labels=None,
            autopct="%1.1f%%",
            colors=colores,
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
            ncol=1,
            fontsize=9,
            frameon=False,
            labelcolor=self.TEXT_MUTED
        )

        fig.tight_layout(pad=1.5)
        self._embed_figura(fig, cuerpo)
        return card

    # ══════════════════════════════════════════════════════
    # GRÁFICO: MOVIMIENTOS POR MES
    # ══════════════════════════════════════════════════════
    def _grafico_barras_por_mes(self, parent, datos):
        card, cuerpo = self._card(parent, "Movimientos por mes")

        meses  = [d["mes"] for d in datos]
        deudas = [d["deuda"] for d in datos]
        abonos = [d["abono"] for d in datos]

        # ancho dinámico según cantidad de meses
        ancho = max(11, len(meses) * 0.9)

        fig = self._figura(ancho, 3.8)
        ax  = fig.add_subplot(111)
        self._estilo_ax(ax)

        x = range(len(meses))
        w = 0.38
        ax.bar(x, deudas, width=w, label="Deuda",   color=self.ACCENT_RED,   alpha=0.9)
        ax.bar([i + w for i in x], abonos, width=w, label="Ingreso", color=self.ACCENT_GREEN, alpha=0.9)

        ax.set_xticks([i + w / 2 for i in x])
        ax.set_xticklabels(meses, rotation=40, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.15, color="#475569")
        ax.legend(fontsize=9, frameon=False, labelcolor=self.TEXT_MUTED)

        # contenedor con scroll horizontal
        scroll_frame = tk.Frame(cuerpo, bg=self.CARD)
        scroll_frame.pack(fill="both", expand=True)

        h_scroll = ttk.Scrollbar(
            scroll_frame,
            orient="horizontal",
            style="Thin.Horizontal.TScrollbar"
        )
        h_scroll.pack(side="bottom", fill="x")

        canvas_fig = FigureCanvasTkAgg(fig, scroll_frame)
        widget = canvas_fig.get_tk_widget()
        widget.pack(side="top", fill="both", expand=True)

        # vincular scroll horizontal al canvas de matplotlib
        h_scroll.configure(command=lambda *a: widget.xview(*a))
        widget.configure(xscrollcommand=h_scroll.set)

        sc = self._scroll_canvas
        widget.bind("<MouseWheel>", lambda e: sc.yview_scroll(int(-1*(e.delta/120)), "units"))
        widget.bind("<Button-4>",   lambda e: sc.yview_scroll(-1, "units"))
        widget.bind("<Button-5>",   lambda e: sc.yview_scroll(1,  "units"))

        return card

    # ══════════════════════════════════════════════════════
    # TABLA: DEUDAS MÁS ANTIGUAS
    # ══════════════════════════════════════════════════════
    def _tabla_deudas_antiguas(self, parent, datos):
        card, cuerpo = self._card(parent, "Deudas más antiguas sin pagar")

        cols = ("cliente", "fecha", "monto")
        tabla = ttk.Treeview(
            cuerpo,
            columns=cols,
            show="headings",
            style="Dark.Treeview",
            height=min(len(datos), 8)
        )

        tabla.heading("cliente", text="Cliente")
        tabla.heading("fecha",   text="Desde")
        tabla.heading("monto",   text="Monto pendiente")

        tabla.column("cliente", width=280, anchor="w")
        tabla.column("fecha",   width=160, anchor="center")
        tabla.column("monto",   width=180, anchor="e")

        tabla.tag_configure("par",   background="#243044")
        tabla.tag_configure("impar", background=self.CARD)

        for i, d in enumerate(datos):
            tag = "par" if i % 2 == 0 else "impar"
            tabla.insert(
                "", "end",
                values=(
                    d["cliente"],
                    d["fecha"],
                    f"${d['monto']:,.0f}"
                ),
                tags=(tag,)
            )

        # scrollbar vertical interna minimalista
        scroll_tabla = ttk.Scrollbar(
            cuerpo,
            orient="vertical",
            command=tabla.yview,
            style="Thin.Vertical.TScrollbar"
        )
        tabla.configure(yscrollcommand=scroll_tabla.set)

        scroll_tabla.pack(side="right", fill="y")
        tabla.pack(side="left", fill="both", expand=True)
        return card