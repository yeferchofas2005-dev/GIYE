import tkinter as tk

from vista.panel_dashboard import panel_dashboard
from vista.panel_inicio import panel_inicio

class Ventana(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GYIE - Gestion Yalejo de Ingresos y Egresos.")

        # Fullscreen con bordes
        #Linux
        self.attributes("-zoomed", True)
        #Windows
        #self.state("zoomed")

        # Contenedor principal donde cargan los paneles
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)

        self.panel_actual = None

        #callback para manejar clicks en transacciones
        self.on_click_transaccion = None

    # ==============================
    # Metodo para cambiar de panel
    # ==============================
    def _cambiar_panel(self, nuevo_panel):
        """Oculta el panel actual y muestra uno nuevo."""
        if self.panel_actual is not None:
            self.panel_actual.pack_forget()

        self.panel_actual = nuevo_panel
        self.panel_actual.pack(fill="both", expand=True)

    # ==============================
    # Metodo para click de las transacciones
    # ==============================
    def set_on_click_transaccion(self, callback):
        self.on_click_transaccion = callback

    # ==============================
    # PANEL DE INICIO (con callbacks registrados)
    # ==============================
    def set_panel_inicio(self, on_admin, on_empleado):
        panel = panel_inicio(self.contenedor, on_admin=on_admin, on_empleado=on_empleado)
        self._cambiar_panel(panel)

    # ==============================
    # PANEL PRINCIPAL (Dashboard)
    # ==============================
    def set_panel_dashboard(self, datos_tabla, total_deuda, total_abono, on_nuevo_abono, on_nueva_deuda, on_filtrar):
        panel = panel_dashboard(
            self.contenedor,
            datos_tabla,
            total_deuda,
            total_abono,
            on_nuevo_abono=on_nuevo_abono,
            on_nueva_deuda=on_nueva_deuda,
            on_filtrar=on_filtrar
        )
        panel.on_filtrar_callback = on_filtrar

        #Pasamos el callback de click de transaccion
        panel.master.on_click_transaccion = self.on_click_transaccion

        self._cambiar_panel(panel)

