import tkinter as tk

from vista.panel_inicio import panel_inicio
from vista.panel_dashboard import panel_dashboard
from vista.panel_administrador import panel_administrador
from vista.panel_administrador_empleado import panel_administrador_empleado
from vista.panel_administrador_backup import panel_administrador_backup

class Ventana(tk.Tk):
    """
    Ventana principal de la aplicación GYIE.

    Esta clase actúa como el contenedor raíz de la interfaz gráfica.
    Se encarga de:
    - Inicializar la ventana principal
    - Gestionar el cambio entre paneles (frames)
    - Centralizar callbacks compartidos entre vistas
    """

    def __init__(self):
        """
        Inicializa la ventana principal.

        Configura:
        - Título de la aplicación
        - Modo pantalla completa
        - Contenedor principal para los paneles
        - Variables de control del panel activo y callbacks globales
        """
        super().__init__()

        self.title("GYIE - Gestion Yalejo de Ingresos y Egresos.")

        # Fullscreen con bordes
        # Linux
        self.attributes("-zoomed", True)
        # Windows
        # self.state("zoomed")

        # Contenedor principal donde se cargan los paneles
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)

        # Referencia al panel actualmente visible
        self.panel_actual = None

        # Callback global para manejar clicks en transacciones
        self.on_click_transaccion = None

    # ==============================
    # CAMBIO DE PANEL
    # ==============================
    def _cambiar_panel(self, nuevo_panel):
        """
        Cambia el panel actualmente visible.

        Este método:
        - Oculta el panel actual (si existe)
        - Muestra el nuevo panel recibido

        Args:
            nuevo_panel (tk.Frame): Panel que se mostrará en la ventana
        """
        if self.panel_actual is not None:
            self.panel_actual.pack_forget()

        self.panel_actual = nuevo_panel
        self.panel_actual.pack(fill="both", expand=True)

    # ==============================
    # CALLBACK GLOBAL DE TRANSACCIONES
    # ==============================
    def set_on_click_transaccion(self, callback):
        """
        Registra un callback global para manejar clicks en transacciones.

        Este callback será utilizado por paneles que necesiten
        reaccionar al click sobre una transacción específica.

        Args:
            callback (callable): Función que maneja el evento de click
        """
        self.on_click_transaccion = callback

    # ==============================
    # PANEL DE INICIO
    # ==============================
    def set_panel_inicio(self, on_admin, on_empleado):
        """
        Carga el panel de inicio de la aplicación.

        Este panel permite seleccionar el tipo de acceso:
        - Administrador
        - Empleado

        Args:
            on_admin (callable): Callback para login de administrador
            on_empleado (callable): Callback para login de empleado
        """
        panel = panel_inicio(
            self.contenedor,
            on_admin=on_admin,
            on_empleado=on_empleado
        )
        self._cambiar_panel(panel)

    # ==============================
    # PANEL DASHBOARD
    # ==============================
    def set_panel_dashboard(
        self,
        datos_tabla,
        total_deuda,
        total_abono,
        on_nuevo_abono,
        on_nueva_deuda,
        on_filtrar,
        on_trachar,
        on_regresar
    ):
        """
        Carga el panel principal (Dashboard).

        Muestra:
        - Tabla de transacciones
        - Totales de deuda y abonos
        - Acciones principales del sistema

        Args:
            datos_tabla (list): Datos a mostrar en la tabla
            total_deuda (float | int): Total de deudas acumuladas
            total_abono (float | int): Total de abonos realizados
            on_nuevo_abono (callable): Crear nuevo abono
            on_nueva_deuda (callable): Crear nueva deuda
            on_filtrar (callable): Filtrar transacciones
            on_trachar (callable): Tachar o marcar transacción
            on_regresar (callable): Volver al panel anterior
        """
        panel = panel_dashboard(
            self.contenedor,
            datos_tabla,
            total_deuda,
            total_abono,
            on_nuevo_abono=on_nuevo_abono,
            on_nueva_deuda=on_nueva_deuda,
            on_filtrar=on_filtrar,
            on_tachar=on_trachar,
            on_regresar=on_regresar
        )

        # Registramos callback de filtrado
        panel.on_filtrar_callback = on_filtrar

        # Pasamos el callback global de transacciones
        panel.master.on_click_transaccion = self.on_click_transaccion

        self._cambiar_panel(panel)

    # ==============================
    # PANEL ADMINISTRADOR
    # ==============================
    def set_panel_administrador(
        self,
        on_regresar,
        on_empleados,
        on_backup,
        on_importar_excel,
        on_cambiar_contraseña,
        on_estadisticas
    ):
        """
        Carga el panel de administración del sistema.

        Este panel permite acceder a:
        - Gestión de empleados
        - Backups del sistema
        - Importación de datos
        - Configuración de seguridad
        - Estadísticas generales

        Args:
            on_regresar (callable): Volver al panel de inicio
            on_empleados (callable): Gestión de empleados
            on_backup (callable): Crear/restaurar backups
            on_importar_excel (callable): Importar datos desde Excel
            on_cambiar_contraseña (callable): Cambiar contraseña del administrador
            on_estadisticas (callable): Mostrar estadísticas del sistema
        """
        panel = panel_administrador(
            self.contenedor,
            on_regresar=on_regresar,
            on_empleados=on_empleados,
            on_backup=on_backup,
            on_importar_excel=on_importar_excel,
            on_cambiar_contraseña=on_cambiar_contraseña,
            on_estadisticas=on_estadisticas
        )

        self._cambiar_panel(panel)

    # ==============================
    # PANEL ADMINISTRADOR - EMPLEADOS
    # ==============================
    def set_panel_administrador_empleado(
        self,
        empleados,
        on_agregar,
        on_editar,
        on_eliminar,
        on_regresar
    ):
        """
        Carga el panel de gestión de empleados.

        Permite realizar operaciones CRUD sobre los empleados:
        - Agregar
        - Editar
        - Eliminar

        Args:
            empleados (list): Lista de empleados a mostrar
            on_agregar (callable): Agregar nuevo empleado
            on_editar (callable): Editar empleado seleccionado
            on_eliminar (callable): Eliminar empleado seleccionado
            on_regresar (callable): Volver al panel administrador
        """
        panel = panel_administrador_empleado(
            self.contenedor,
            empleados=empleados,
            on_agregar=on_agregar,
            on_editar=on_editar,
            on_eliminar=on_eliminar,
            on_regresar=on_regresar
        )

        self._cambiar_panel(panel)

    # ==============================
    # PANEL ADMINISTRADOR - EMPLEADOS
    # ==============================
    def set_panel_administrador_backup(
        self,
        correo_backup,
        on_cambiar_correo,
        on_generar_backup,
        on_regresar
    ):
        """
        Carga el panel de administración de backups.

        Permite gestionar:
        - Correo destino de los backups
        - Generación de nuevos backups
        - Restauración desde backups

        Args:
            correo_backup (str): Correo destino actual de los backups
            on_cambiar_correo (callable): Cambiar correo destino
            on_generar_backup (callable): Generar nuevo backup
            on_regresar (callable): Volver al panel administrador
        """
        panel = panel_administrador_backup(
            self.contenedor,
            correo_backup=correo_backup,
            on_cambiar_correo=on_cambiar_correo,
            on_generar_backup=on_generar_backup,
            on_regresar=on_regresar
        )

        self._cambiar_panel(panel)
