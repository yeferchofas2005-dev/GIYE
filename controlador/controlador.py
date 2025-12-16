from vista.ventana import Ventana
from vista.ventana_emergente import ventana_emergente

from modelo.cliente import Cliente
from modelo.transaccion import Transaccion
from modelo.datos_configuracion import DatosConfiguracion
from modelo.filtros import Filtros

from datetime import datetime


class Controller:
    """
    Controlador principal de la aplicación (patrón MVC).
    - Coordina la vista (Ventana y paneles) con los modelos (Cliente, Transaccion, etc.)
    - Contiene la lógica de interacción de alto nivel (login, registrar transacciones, filtros, etc.)
    - NO realiza operaciones de UI directamente (las delega a ventana_emergente / Ventana).
    """

    def __init__(self):
        """
        Inicialización del controlador:
        - Crea la ventana principal (vista).
        - Inicializa variables que guardan el empleado en turno.
        - Registra el callback para clicks sobre una transacción en la vista.
        """
        self.ventana = Ventana()                     # Instancia la GUI principal
        self.empleado_en_turno = None                # Diccionario/registro del empleado que inició sesión
        self.id_empleado_en_turno = None             # id del empleado en turno (int)
        # Cuando se haga click en una fila de transacción, la vista llamará a mostrar_detalles_transaccion
        self.ventana.set_on_click_transaccion(self.mostrar_detalles_transaccion)

    def iniciar(self):
        """
        Inicia la aplicación:
        - Configura el panel de inicio (pasa callbacks para admin y empleado).
        - Llama al mainloop de Tkinter para empezar el bucle de eventos.
        """
        self.ventana.set_panel_inicio(
            on_admin=self.login_admin,
            on_empleado=self.login_empleado
        )
        self.ventana.mainloop()

    def regresar_inicio(self):
        self.ventana.set_panel_inicio(
            on_admin=self.login_admin,
            on_empleado=self.login_empleado
        )

    # ---------------------------------------------------------------------
    # CARGA Y ACTUALIZACIÓN DEL DASHBOARD
    # ---------------------------------------------------------------------
    # Metodo para cargar el dashboard al iniciar la aplicacion
    def recargar_dashboard(self):
        """
        Crea y envía los datos necesarios al panel dashboard:
        - Consulta todas las transacciones.
        - Construye datos_tabla con las tuplas esperadas por la vista.
        - Calcula totales (deuda / abonos).
        - Formatea los totales para visualización (separador de miles con puntos).
        - Llama a set_panel_dashboard con callbacks para acciones del usuario.
        """
        transacciones = Transaccion.obtener_todas()

        datos_tabla = []
        total_deuda = 0
        total_abonos = 0

        # Recorremos cada transacción para construir la tabla y acumular totales
        for transaccion in transacciones:

            # obtener nombre del cliente asociado a la transacción
            nombre = Cliente.obtener_nombre_por_id(transaccion['id_cliente'])

            # formateo de fecha (se asume que fecha_creacion es un datetime)
            fecha = transaccion['fecha_creacion'].strftime("%Y-%m-%d-%H:%M:%S")

            tipo = transaccion['tipo_transaccion']         # "DEUDA" o "INGRESO"
            monto = int(transaccion['monto'])              # monto convertido a int para cálculos
            accion = ""

            estado_deuda = transaccion["estado_deuda"]     # "PENDIENTE", "CANCELADA", etc.

            if tipo == "DEUDA":
                # Si es deuda, la columna 'debe' recibe el monto
                debe = monto
                abono = 0

                # Si la deuda está pendiente, la sumamos al total de deuda
                if estado_deuda == "PENDIENTE":
                    total_deuda += monto

                # Acción visible en la tabla (permite tachar)
                accion = "Tachar"
            else:
                # Si no es deuda, se considera ingreso/abono
                debe = 0
                abono = monto
                total_abonos += monto
                accion = "---"

            # Agregamos la fila a los datos que recibirá la vista.
            # La vista espera: (id_transaccion, nombre, debe, abono, fecha, accion, estado_deuda)
            datos_tabla.append((transaccion["id_transaccion"], nombre, debe, abono, fecha, accion, estado_deuda))

        # Separamos los dígitos de los totales con puntos (ej. 2000000 -> "2.000.000") para mostrar al usuario
        total_abonos_formateado = f'{total_abonos:,}'.replace(',', '.')
        total_deudas_formateado = f'{total_deuda:,}'.replace(',', '.')

        # Enviamos todo al panel dashboard junto con los callbacks para acciones del UI
        self.ventana.set_panel_dashboard(
            datos_tabla,
            total_deudas_formateado,
            total_abonos_formateado,
            on_nuevo_abono=self.registrar_nuevo_abono,
            on_nueva_deuda=self.registrar_nueva_deuda,
            on_filtrar=self.aplicar_filtros,
            on_trachar=self.tachar_deuda,
            on_regresar=self.regresar_inicio
        )

    # Metodo para actualizar dashboard usando filtros
    def _filtrar_dashboard(self, transacciones):
        """
        Similar a recargar_dashboard, pero recibe una lista de transacciones ya filtradas.
        Se encarga de:
        - Construir datos_tabla para la vista a partir de la lista filtrada.
        - Recalcular totales (sin formatear aquí).
        - Llamar a set_panel_dashboard proporcionando los mismos callbacks.
        Nota: este método no aplica filtros; recibe la lista resultante.
        """
        datos_tabla = []
        total_deuda = 0
        total_abonos = 0

        for transaccion in transacciones:
            nombre = Cliente.obtener_nombre_por_id(transaccion['id_cliente'])
            fecha = transaccion['fecha_creacion'].strftime("%Y-%m-%d-%H:%M:%S")
            tipo = transaccion['tipo_transaccion']
            monto = int(transaccion['monto'])
            accion = ""

            estado_deuda = transaccion["estado_deuda"]

            if tipo == "DEUDA":
                debe = monto
                abono = 0

                if estado_deuda == "PENDIENTE":
                    total_deuda += monto

                accion = "Tachar"
            else:
                debe = 0
                abono = monto
                total_abonos += monto
                accion = "---"

            datos_tabla.append((transaccion["id_transaccion"], nombre, debe, abono, fecha, accion, estado_deuda))

        # Actualiza el panel dashboard (aquí no se formatean los totales; se pasan tal cual)
        self.ventana.set_panel_dashboard(
            datos_tabla,
            total_deuda,
            total_abonos,
            self.registrar_nuevo_abono,
            self.registrar_nueva_deuda,
            self.aplicar_filtros,
            self.tachar_deuda,
            self.regresar_inicio
        )

    # ---------------------------------------------------------------------
    # AUTENTICACIÓN / LOGIN
    # ---------------------------------------------------------------------
    def login_admin(self):
        """
        Handler para el login de administrador.
        Abre panel de administrador, encargado de:
        - Agregar, Eliminar, Editar un empleado.
        - Enviar Backup de la base de datos via mail en formato XLS.
        - Importar datos desde un archivo XLS.
        - Cambiar la contraseña de administrador.
        """
        contraseña = ventana_emergente.pedir_contraseña("Login admin.", "Ingrese la contraseña de administrador:")

        if DatosConfiguracion.comparar_contraseña(contraseña):
            self.ventana.set_panel_administrador(
                on_regresar=self.regresar_inicio,
                on_empleados=self.gestionar_empleados,
                on_backup=self.crear_backup,
                on_importar_excel=self.importar_excel,
                on_cambiar_contraseña=self.cambiar_contraseña_admin,
                on_estadisticas=self.ver_estadisticas
            )
        else:
            ventana_emergente.mostrar_error("Error de Autenticación", "Contraseña de administrador incorrecta.")

    # Login de empleado
    def login_empleado(self):
        """
        Proceso de login para empleado:
        - Obtiene la lista de empleados desde el modelo Cliente.
        - Llama a la ventana emergente para que el usuario seleccione uno.
        - Si se selecciona, guarda el empleado en sesión y recarga el dashboard.
        """
        empleados = Cliente.obtener_empleados()

        # Abre una ventana emergente con un combobox para seleccionar empleado
        empleado = ventana_emergente.seleccionar_de_lista("Selección de Empleado", "Seleccione su nombre de la lista:" ,empleados)

        if empleado is None:
            # Si el usuario canceló la selección
            ventana_emergente.mostrar_advertencia("Selección Cancelada", "No se seleccionó ningún empleado.")
            return

        # Guardar empleado en turno (diccionario que contiene al menos id_cliente y nombre)
        self.empleado_en_turno = empleado
        self.id_empleado_en_turno = empleado['id_cliente']

        # Mensaje de bienvenida
        ventana_emergente.mostrar_informacion("Bienvenido", f"Has iniciado sesión como {empleado['nombre']}.")

        # Cargar el dashboard con las transacciones
        self.recargar_dashboard()

# -------------------------------------------------------------------------
# LOGICA DE DASHBOARD
# -------------------------------------------------------------------------
    # REGISTRO DE TRANSACCIONES
    # ---------------------------------------------------------------------
    # Metodo para registrar un nuevo abono
    def registrar_nuevo_abono(self):
        """
        Abre la ventana para crear un abono:
        - Obtiene lista de clientes.
        - Llama a pedir_datos_transaccion con tipo 'ABONO'.
        - Si el usuario completa el formulario, crea una Transaccion (tipo INGRESO).
        - Muestra confirmación y recarga el dashboard.
        """
        clientes = Cliente.obtener_todos()

        datos = ventana_emergente.pedir_datos_transaccion(
            "Nuevo Abono",
            "ABONO",
            clientes,
            self.agregar_cliente
        )

        if datos is None:
            # Usuario canceló la operación
            return

        # Crear la transacción en BD con la información ingresada
        Transaccion.agregar(
            fecha_creacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            tipo_transaccion="INGRESO",
            subtipo_transaccion=datos["subtipo"],
            monto=datos["monto"],
            id_cliente=datos["id_cliente"],
            id_empleado=self.id_empleado_en_turno,
            descripcion=datos["descripcion"],
            saldo_afectado=datos["monto"],
            estado_deuda='PAGADA'
        )

        ventana_emergente.mostrar_informacion("Éxito", "Abono registrado correctamente.")
        self.recargar_dashboard()

    # Metodo para registrar una nueva deuda
    def registrar_nueva_deuda(self):
        """
        Abre la ventana para crear una deuda:
        - Obtiene lista de clientes.
        - Llama a pedir_datos_transaccion con tipo 'DEUDA'.
        - Si el usuario completa el formulario, crea una Transaccion (tipo DEUDA).
        - Muestra confirmación y recarga el dashboard.
        """
        clientes = Cliente.obtener_todos()

        datos = ventana_emergente.pedir_datos_transaccion(
            "Nueva Deuda",
            "DEUDA",
            clientes,
            self.agregar_cliente
        )

        if datos is None:
            return

        Transaccion.agregar(
            fecha_creacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            tipo_transaccion="DEUDA",
            subtipo_transaccion=datos["subtipo"],
            monto=datos["monto"],
            id_cliente=datos["id_cliente"],
            id_empleado=self.id_empleado_en_turno,
            descripcion=datos["descripcion"],
            saldo_afectado=datos["monto"],
            estado_deuda='PENDIENTE'
        )

        ventana_emergente.mostrar_informacion("Éxito", "Deuda registrada correctamente.")
        self.recargar_dashboard()

    # ---------------------------------------------------------------------
    # GESTIÓN DE CLIENTES
    # ---------------------------------------------------------------------
    def agregar_cliente(self):
        """
        Pide los datos de un nuevo cliente y lo inserta en la base de datos.
        - Abre la ventana para pedir datos del cliente.
        - Si el usuario confirma, guarda en BD y muestra confirmación.
        - Devuelve un diccionario con los datos del cliente insertado para permitir
          que el llamador (p. ej. la ventana de transacción) pueda actualizar su lista.
        """
        # Pedir datos al usuario
        datos_cliente = ventana_emergente.pedir_datos_cliente()

        # Si el usuario canceló
        if not datos_cliente:
            ventana_emergente.mostrar_advertencia("Acción Cancelada", "No se agregaron datos del cliente.")
            return None

        # Guardar en BD (Cliente.agregar debe encargarse de la inserción)
        nuevo_id = Cliente.agregar(
            nombre=datos_cliente["nombre"],
            telefono=datos_cliente["telefono"],
            notas=datos_cliente["notas"],
            empleado=False
        )

        # Mostrar confirmación
        ventana_emergente.mostrar_informacion("Éxito", "Cliente agregado correctamente.")

        # Devolver los datos del nuevo cliente para que la vista pueda refrescarse si lo desea
        return {
            "id_cliente": nuevo_id,
            "nombre": datos_cliente["nombre"],
            "telefono": datos_cliente["telefono"],
            "notas": datos_cliente["notas"]
        }

    # ---------------------------------------------------------------------
    # FILTRADO DE TRANSACCIONES
    # ---------------------------------------------------------------------
    def aplicar_filtros(self, filtros):
        """
        Aplica los filtros solicitados desde la UI y actualiza el dashboard.
        - Recopila todas las transacciones y filtra por fecha, nombre, estado y orden.
        - Para filtros de fecha/nombre/estado usa métodos del módulo Filtros (consultas SQL).
        - Para ordenamientos se filtra por tipo (DEUDA/INGRESO) y se ordena por monto.
        - Llama a _filtrar_dashboard con la lista resultante para renderizarla.
        """
        transacciones = Transaccion.obtener_todas()

        # Filtro por fecha: usamos Filtros.filtrar_por_fecha para obtener transacciones de esa fecha
        if filtros["fecha"]:
            resultado_fecha = Filtros.filtrar_por_fecha(filtros["fecha"])
            ids_fecha = {t["id_transaccion"] for t in resultado_fecha}

            transacciones = [
                t for t in transacciones
                if t["id_transaccion"] in ids_fecha
            ]

        # Filtro por nombre: Filtros.filtrar_por_nombre_cliente devuelve transacciones que coinciden
        if filtros["nombre"]:
            resultado_nombre = Filtros.filtrar_por_nombre_cliente(filtros["nombre"])
            ids_nombre = {t["id_transaccion"] for t in resultado_nombre}

            transacciones = [
                t for t in transacciones
                if t["id_transaccion"] in ids_nombre
            ]

        # Filtro por estado: Todas / Tachadas / Sin tachar
        if filtros["estado"]:
            resultado_estado = Filtros.filtrar_por_estado_deuda(filtros["estado"])
            ids_estado = {t["id_transaccion"] for t in resultado_estado}

            transacciones = [
                t for t in transacciones
                if t["id_transaccion"] in ids_estado
            ]

        # Filtro por orden: hay 4 posibilidades que ordenan y filtran por tipo de transacción
        orden = filtros["orden"]

        if orden == "Abono Mayor a Menor":
            transacciones = [
                t for t in transacciones
                if t["tipo_transaccion"] == "INGRESO"
            ]
            transacciones.sort(key=lambda x: float(x["monto"]), reverse=True)

        elif orden == "Abono Menor a Mayor":
            transacciones = [
                t for t in transacciones
                if t["tipo_transaccion"] == "INGRESO"
            ]
            transacciones.sort(key=lambda x: float(x["monto"]))

        elif orden == "Debe Mayor a Menor":
            transacciones = [
                t for t in transacciones
                if t["tipo_transaccion"] == "DEUDA"
            ]
            transacciones.sort(key=lambda x: float(x["monto"]), reverse=True)

        elif orden == "Debe Menor a Mayor":
            transacciones = [
                t for t in transacciones
                if t["tipo_transaccion"] == "DEUDA"
            ]
            transacciones.sort(key=lambda x: float(x["monto"]))

        # Actualizar dashboard con las transacciones resultantes
        self._filtrar_dashboard(transacciones)

    # ---------------------------------------------------------------------
    # MOSTRAR DETALLES DE UNA TRANSACCIÓN
    # ---------------------------------------------------------------------
    # metodo para mostrar la informacion de la fila seleccionada
    def mostrar_detalles_transaccion(self, valores):
        """
        Muestra un resumen detallado de la transacción seleccionada en la tabla.
        - 'valores' es la tupla (id, cliente, deuda, abono, fecha, ...)
        - Recupera la transacción completa y datos del cliente desde los modelos.
        - Construye un string con los campos relevantes y lo muestra en una ventana.
        """
        # Marcamos variables traidas desde la tabla principal.
        id, cliente, deuda, abono, fecha, _ = valores

        # Consultamos informacion sobre la transaccion y el cliente.
        datos_transaccion = Transaccion.obtener_por_id(id)
        datos_cliente = Cliente.obtener_por_id(datos_transaccion["id_cliente"])

        # Convertimos infoirmacion de la tabla (deuda o bono) a floats.
        deuda = float(deuda)
        abono = float(abono)

        # Construimos el mensaje con la información completa
        datos = (
            "──────── DETALLES DE LA TRANSACCIÓN ────────\n\n"
            f"🧍 Cliente:           {cliente}\n"
            f"📞 Teléfono:          {datos_cliente['telefono']}\n"
            f"🏠 Dirección:         {datos_cliente['notas']}\n"
            "---------------------------------------------\n"
            f"📌 Tipo:              {datos_transaccion['tipo_transaccion']}\n"
            f"📂 Subtipo:           {datos_transaccion['subtipo_transaccion']}\n"
            f"📅 Fecha:             {valores[4]}\n"
            f"💰 Monto:             {abono if abono > 0 else deuda}\n"
            f"📝 Descripción:       {datos_transaccion['descripcion'] if datos_transaccion['descripcion'] else 'N/A'}\n"
            f"📊 Estado de Deuda:   {datos_transaccion['estado_deuda']}\n"
            f"👨‍💼 Encargado por:    {Cliente.obtener_nombre_por_id(datos_transaccion['id_empleado'])}\n"
            "─────────────────────────────────────────────"
        )

        # Mostramos en la ventana la informacion
        ventana_emergente.mostrar_informacion_transaccion("Datos transaccion", datos)

    # ---------------------------------------------------------------------
    # TACHAR / MARCAR DEUDA COMO PAGADA
    # ---------------------------------------------------------------------
    # Metodo para tachar una deuda como pagada
    def tachar_deuda(self, id_transaccion):
        """
        Marca una deuda como 'CANCELADA' (tachada) tras diversas comprobaciones:
        - Si la deuda pertenece a un empleado, se requiere contraseña de administrador.
        - Pide confirmación al usuario.
        - Si todo es correcto, actualiza el estado en la base de datos y recarga el dashboard.
        """
        transaccion = Transaccion.obtener_por_id(id_transaccion)

        # Si la transacción pertenece a un empleado, no permitimos marcarla sin validar.
        if Cliente.es_empleado(transaccion["id_cliente"]):
            ventana_emergente.mostrar_advertencia("Acción No Permitida", "No puedes tachar una deuda de un empleado.")
            contraseña_admin = ventana_emergente.pedir_contraseña("Ingrese contrasela de administrador para continuar:", "Autenticación Requerida")

            # Verificamos la contraseña con los datos de configuración
            if not contraseña_admin or not DatosConfiguracion.comparar_contraseña(contraseña_admin):
                ventana_emergente.mostrar_error("Autenticación Fallida", "Contraseña de administrador incorrecta. No se puede tachar la deuda.")
                return

        # Preguntamos en ventana emergente si se confirma la acción
        confirmar = ventana_emergente.preguntar_confirmacion("Confirmar Tachar Deuda", "¿Estás seguro de que deseas marcar esta deuda como PAGADA?")

        # Si el usuario no confirma, salimos
        if not confirmar:
            return

        # Actualizamos el estado de la transacción en la BD
        Transaccion.actualizar_estado(id_transaccion, "CANCELADA")

        ventana_emergente.mostrar_informacion("Éxito", "La deuda ha sido cancelada correctamente !")

        # Recargamos el dashboard para reflejar el cambio
        self.recargar_dashboard()

# -------------------------------------------------------------------------
# LOGICA DE DASHBOARD
# -------------------------------------------------------------------------
    #Gestio0n de empleados
    def gestionar_empleados(self):
        print("Gestionar empleados")
    
    #Crear backup
    def crear_backup(self):
        print("Crear backup")

    #Importar desde excel
    def importar_excel(self):
        print("Importar desde excel")

    #Cambiar contraseña admin
    def cambiar_contraseña_admin(self):
        print("Cambiar contraseña admin")

    #Ver estadísticas
    def ver_estadisticas(self):
        print("Ver estadísticas")