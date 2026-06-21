import os

from vista.ventana import Ventana
from vista.ventana_emergente import ventana_emergente

from modelo.cliente import Cliente
from modelo.filtros import Filtros
from modelo.transaccion import Transaccion
from modelo.datos_configuracion import DatosConfiguracion
from modelo.gestion_archivos import gestion_archivos
from modelo.enviador_mensajes import enviador_mensajes
from modelo.datos_graficas import datos_graficas

from datetime import datetime


class Controller:
    """
    Controlador principal del sistema GYIE, implementado bajo el patrón
    Modelo – Vista – Controlador (MVC).

    FUNCIÓN GENERAL:
    ----------------
    Este controlador actúa como el núcleo de coordinación de la aplicación.
    Su responsabilidad principal es orquestar la comunicación entre:

    - La capa de presentación (Vista)
    - La capa de lógica y persistencia (Modelos)
    - Las acciones del usuario (eventos, botones, formularios)

    El Controller NO contiene lógica de interfaz gráfica ni lógica de acceso
    directo a la base de datos. Su función es decidir:
    - QUÉ datos se solicitan
    - CUÁNDO se solicitan
    - A QUÉ vista se envían
    - QUÉ acción ejecutar ante una interacción del usuario

    ------------------------------------------------------------
    RESPONSABILIDADES PRINCIPALES:
    ------------------------------------------------------------

    1. GESTIÓN DE NAVEGACIÓN
       ---------------------
       - Controla el flujo entre paneles:
         * Inicio
         * Dashboard
         * Panel administrador
         * Panel de empleados
         * Panel de estadísticas
         * Panel de backups
       - Decide cuándo cambiar de vista y con qué información hacerlo

    2. COORDINACIÓN DEL DASHBOARD
       ---------------------------
       - Carga y transforma las transacciones para visualización
       - Calcula totales de deuda y abonos
       - Formatea la información para que la vista no procese datos
       - Responde a acciones del dashboard:
         * Registrar deudas
         * Registrar abonos
         * Aplicar filtros
         * Tachado de deudas
         * Visualización de detalles

    3. AUTENTICACIÓN Y CONTROL DE ACCESO
       ---------------------------------
       - Gestiona login de administrador y empleados
       - Mantiene el estado de sesión del empleado en turno
       - Protege acciones sensibles (tachado de deudas de empleados,
         cambios de configuración, backups, etc.)

    4. GESTIÓN DE TRANSACCIONES
       ------------------------
       - Registra nuevas deudas y abonos
       - Asocia transacciones a clientes y empleados
       - Controla estados de deuda (PENDIENTE, CANCELADA)
       - Garantiza consistencia antes de escribir en base de datos

    5. GESTIÓN DE CLIENTES Y EMPLEADOS
       --------------------------------
       - Alta, edición y eliminación de clientes
       - Gestión completa de empleados desde el panel administrador
       - Sincroniza cambios con la vista tras cada operación

    6. FILTRADO Y ORDENAMIENTO DE INFORMACIÓN
       --------------------------------------
       - Aplica filtros combinados:
         * Fecha
         * Nombre de cliente
         * Estado de deuda
         * Orden por monto
       - Delega consultas especializadas al modelo `Filtros`
       - Re-renderiza el dashboard con resultados filtrados

    7. GESTIÓN DE ESTADÍSTICAS
       -----------------------
       - Obtiene datos estadísticos agregados desde `datos_graficas`
       - Envía información lista para graficar a la vista
       - No genera gráficos, solo coordina datos y navegación

    8. BACKUPS E IMPORTACIÓN DE DATOS
       ------------------------------
       - Coordina la generación de backups manuales
       - Gestiona exportación a Excel
       - Orquesta el envío de correos con adjuntos
       - Controla la importación segura de datos desde backups válidos

    9. CONFIGURACIÓN DEL SISTEMA
       -------------------------
       - Cambio de contraseña de administrador
       - Gestión del correo de destino de backups
       - Centraliza configuraciones críticas del sistema

    ------------------------------------------------------------
    PRINCIPIOS DE DISEÑO APLICADOS:
    ------------------------------------------------------------

    - Patrón MVC estricto
    - Separación de responsabilidades
    - Bajo acoplamiento entre capas
    - Alta cohesión de responsabilidades
    - Controlador como orquestador, no como procesador

    ------------------------------------------------------------
    RELACIÓN CON OTRAS CAPAS:
    ------------------------------------------------------------

    MODELOS:
    - Cliente
    - Transaccion
    - Filtros
    - DatosConfiguracion
    - datos_graficas
    - gestion_archivos
    - enviador_mensajes

    VISTAS:
    - Ventana principal
    - Paneles administrativos
    - Ventanas emergentes (input / confirmación / alertas)

    ------------------------------------------------------------
    NOTA FINAL:
    ------------------------------------------------------------
    Este controlador está diseñado para ser:
    - Escalable
    - Mantenible
    - Fácil de extender (nuevos reportes, paneles o reglas)
    sin necesidad de modificar la lógica existente.
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
        #self.ventana.set_titulo(f"GYIE - Gestión de Deudas y Abonos - Empleado: {self.id_empleado_en_turno}".format(self.empleado_en_turno['nombre'] if self.empleado_en_turno else "No identificado"))
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
        total_nequi = 0

        # Recorremos cada transacción para construir la tabla y acumular totales
        for transaccion in transacciones:

            # obtener nombre del cliente asociado a la transacción
            nombre = Cliente.obtener_nombre_por_id(transaccion['id_cliente'])

            # formateo de fecha (se asume que fecha_creacion es un datetime)
            fecha = transaccion['fecha_creacion'].strftime("%Y-%m-%d-%H:%M:%S")

            tipo = transaccion['tipo_transaccion']         # "DEUDA" o "INGRESO"
            monto = int(transaccion['monto'])              # monto convertido a int para cálculos
            subtipo = transaccion["subtipo_transaccion"]
            estado_deuda = transaccion["estado_deuda"]     # "PENDIENTE", "CANCELADA", etc.
            accion = ""

            if tipo == "DEUDA":

                debe = monto
                abono = 0

                if estado_deuda == "PENDIENTE":
                    total_deuda += monto

                # ==========================
                # DEUDA NEQUI YA RECIBIDA
                # ==========================
                elif estado_deuda in ["CANCELADA", "PAGADA"] and subtipo == "NEQUI_RECIBIDO":
                    total_nequi += monto

                accion = "Tachar"

            else:

                debe = 0
                abono = monto

                # ==========================
                # MOVIMIENTOS NEQUI
                # ==========================
                if subtipo == "NEQUI_RECIBIDO":
                    total_nequi += monto

                # ==========================
                # DINERO REAL EN CAJA
                # ==========================
                else:
                    total_abonos += monto

                accion = "---"

            # Agregamos la fila a los datos que recibirá la vista.
            # La vista espera: (id_transaccion, nombre, debe, abono, fecha, accion, estado_deuda)
            datos_tabla.append(
                (
                    transaccion["id_transaccion"],
                    nombre,
                    debe,
                    abono,
                    fecha,
                    accion,
                    estado_deuda,
                    subtipo
                )
            )

        # Separamos los dígitos de los totales con puntos (ej. 2000000 -> "2.000.000") para mostrar al usuario
        total_abonos_formateado = f'{total_abonos:,}'.replace(',', '.')
        total_deudas_formateado = f'{total_deuda:,}'.replace(',', '.')
        total_nequi_formateado = f'{total_nequi:,}'.replace(',', '.')

        # Enviamos todo al panel dashboard junto con los callbacks para acciones del usuario
        self.ventana.set_panel_dashboard(
            datos_tabla,
            total_deudas_formateado,
            total_abonos_formateado,
            total_nequi_formateado,
            on_nuevo_abono=self.registrar_nuevo_abono,
            on_nueva_deuda=self.registrar_nueva_deuda,
            on_filtrar=self.aplicar_filtros,
            on_tachar=self.tachar_deuda,
            on_regresar=self.regresar_inicio
        )
        
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
        total_nequi = 0

        for transaccion in transacciones:
            nombre = Cliente.obtener_nombre_por_id(transaccion['id_cliente'])
            fecha = transaccion['fecha_creacion'].strftime("%Y-%m-%d-%H:%M:%S")
            tipo = transaccion['tipo_transaccion']
            monto = int(transaccion['monto'])
            subtipo = transaccion["subtipo_transaccion"]
            estado_deuda = transaccion["estado_deuda"]
            accion = ""

            if tipo == "DEUDA":

                debe = monto
                abono = 0

                if estado_deuda == "PENDIENTE":
                    total_deuda += monto

                # ==========================
                # DEUDA NEQUI YA RECIBIDA
                # ==========================
                elif estado_deuda in ["CANCELADA", "PAGADA"] and subtipo == "NEQUI_RECIBIDO":
                    total_nequi += monto

                accion = "Tachar"

            else:

                debe = 0
                abono = monto

                # ==========================
                # MOVIMIENTOS NEQUI
                # ==========================
                if subtipo == "NEQUI_RECIBIDO":
                    total_nequi += monto

                # ==========================
                # DINERO REAL EN CAJA
                # ==========================
                else:
                    total_abonos += monto

                accion = "---"

            datos_tabla.append(
                (
                    transaccion["id_transaccion"],
                    nombre,
                    debe,
                    abono,
                    fecha,
                    accion,
                    estado_deuda,
                    subtipo
                )
            )

        total_abonos_formateado = f'{total_abonos:,}'.replace(',', '.')
        total_deuda_formateado = f'{total_deuda:,}'.replace(',', '.')
        total_nequi_formateado = f'{total_nequi:,}'.replace(',', '.')

        self.ventana.set_panel_dashboard(
            datos_tabla,
            total_deuda_formateado,
            total_abonos_formateado,
            total_nequi_formateado,
            on_nuevo_abono=self.registrar_nuevo_abono,
            on_nueva_deuda=self.registrar_nueva_deuda,
            on_filtrar=self.aplicar_filtros,
            on_tachar=self.tachar_deuda,
            on_regresar=self.regresar_inicio
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

        #Parar el proceso en caso que el usuario no ingrese contrazeñ.
        if contraseña is None:
            ventana_emergente.mostrar_error("Error!", "Debe ingresar una contraseña.")
            return
    
        if DatosConfiguracion.comparar_contraseña(contraseña):
            self.ventana.set_panel_administrador(
                on_regresar=self.regresar_inicio,
                on_empleados=self.gestionar_empleados,
                on_backup=self.cargar_backup,
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
        self.ventana.set_titulo(f"GYIE - Gestión de Deudas y Abonos - Empleado: {empleado['nombre']}")

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

        # Devolver los datos del nuevo cliente para que la vista pueda refrescarse.
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
        id, cliente, deuda, abono, fecha, _, _, _ = valores

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
            f"🪢 Referencia:        {datos_transaccion['referencia_original'] if datos_transaccion['referencia_original'] else 'N/A'}\n"
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
        Marca una deuda como pagada.

        Reglas:
        - NEQUI_PENDIENTE:
            Solo se cancela la deuda.
            No se generan movimientos adicionales.

        - FIADO / PRESTAMO:
            Se pregunta si pagó por Nequi.
            Si paga por Nequi:
                Solo se cancela la deuda.
            Si paga en efectivo:
                Se cancela la deuda y se genera un PAGO_DEUDA.
        """

        transaccion = Transaccion.obtener_por_id(id_transaccion)

        # Validación para empleados
        if Cliente.es_empleado(transaccion["id_cliente"]):

            ventana_emergente.mostrar_advertencia(
                "Acción No Permitida",
                "No puedes tachar una deuda de un empleado."
            )

            contraseña_admin = ventana_emergente.pedir_contraseña(
                "Ingrese contraseña de administrador para continuar:",
                "Autenticación Requerida"
            )

            if not contraseña_admin or not DatosConfiguracion.comparar_contraseña(contraseña_admin):
                ventana_emergente.mostrar_error(
                    "Autenticación Fallida",
                    "Contraseña de administrador incorrecta. No se puede tachar la deuda."
                )
                return

        confirmar = ventana_emergente.preguntar_confirmacion(
            "Confirmar Tachar Deuda",
            "¿Estás seguro de que deseas marcar esta deuda como PAGADA?"
        )

        if not confirmar:
            return

        # --------------------------------------------------------
        # CASO 1: DEUDA QUE NACIÓ COMO NEQUI_PENDIENTE
        # --------------------------------------------------------
        if transaccion["subtipo_transaccion"] == "NEQUI_PENDIENTE":

            Transaccion.actualizar_estado(id_transaccion, "CANCELADA")
            Transaccion.actualizar_subtipo(id_transaccion, "NEQUI_RECIBIDO")

            ventana_emergente.mostrar_informacion(
                "Éxito",
                "La deuda Nequi ha sido cancelada correctamente."
            )

            self.recargar_dashboard()
            return

        # --------------------------------------------------------
        # CASO 2: FIADO / PRESTAMO
        # --------------------------------------------------------
        pago_por_nequi = ventana_emergente.preguntar_confirmacion(
            "Forma de pago",
            "¿La deuda fue pagada por Nequi?"
        )

        # --------------------------------------------------------
        # PAGÓ POR NEQUI
        # --------------------------------------------------------
        if pago_por_nequi:

            Transaccion.actualizar_estado(id_transaccion, "CANCELADA")

            Transaccion.agregar(
                fecha_creacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                tipo_transaccion="INGRESO",
                subtipo_transaccion="NEQUI_RECIBIDO",
                monto=transaccion["monto"],
                id_cliente=transaccion["id_cliente"],
                id_empleado=self.id_empleado_en_turno,
                descripcion=f"PAGO POR NEQUI DE DEUDA DEL DIA {transaccion['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')}",
                saldo_afectado=transaccion["monto"],
                estado_deuda="PAGADA"
            )

            ventana_emergente.mostrar_informacion(
                "Éxito",
                "La deuda fue cancelada correctamente por Nequi."
            )

            self.recargar_dashboard()
            return

        # --------------------------------------------------------
        # PAGÓ EN EFECTIVO
        # --------------------------------------------------------
        Transaccion.actualizar_estado(id_transaccion, "CANCELADA")

        Transaccion.agregar(
            fecha_creacion=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            tipo_transaccion="INGRESO",
            subtipo_transaccion="PAGO_DEUDA",
            monto=transaccion["monto"],
            id_cliente=transaccion["id_cliente"],
            id_empleado=self.id_empleado_en_turno,
            descripcion=f"SE PAGO DEUDA DEL DIA {transaccion['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')}",
            saldo_afectado=transaccion["monto"],
            estado_deuda='PAGADA'
        )

        ventana_emergente.mostrar_informacion(
            "Éxito",
            "La deuda ha sido cancelada correctamente."
        )

        self.recargar_dashboard()

# -------------------------------------------------------------------------
# LOGICA DE PANEL ADMINISTRADOR
# -------------------------------------------------------------------------
   
    # GESTIÓN DE EMPLEADOS
    def gestionar_empleados(self):
        """
        Carga el módulo de gestión de empleados.

        - Obtiene la lista de empleados desde la base de datos
        - Inicializa el panel de administración de empleados
        - Inyecta las funciones del controlador para CRUD
        """
        # Obtener todos los empleados desde el modelo
        empleados = Cliente.obtener_empleados()

        # Cargar el panel de administración de empleados
        # y pasarle los callbacks del controlador
        self.ventana.set_panel_administrador_empleado(
            empleados,
            self.agregar_empleado,
            self.editar_empleado,
            self.eliminar_empleado,
            self.regresar_inicio
        )

    # AGREGAR EMPLEADO
    def agregar_empleado(self):
        """
        Solicita los datos de un nuevo empleado,
        los guarda en la base de datos y devuelve
        el empleado creado para actualizar la vista.
        """
        # Pedir datos al usuario mediante ventana emergente
        datos_empleado = ventana_emergente.pedir_datos_cliente()

        # Si el usuario cancela o no ingresa datos
        if not datos_empleado:
            ventana_emergente.mostrar_advertencia(
                "Acción Cancelada",
                "No se agregaron datos del empleado."
            )
            return None

        # Guardar el nuevo empleado en la base de datos
        Cliente.agregar(
            nombre=datos_empleado["nombre"],
            telefono=datos_empleado["telefono"],
            notas=datos_empleado["notas"],
            empleado=True
        )

        # Confirmación visual al usuario
        ventana_emergente.mostrar_informacion(
            "Éxito",
            "Empleado agregado correctamente."
        )

        # Refrescamos panel de gestion de empleados
        self.gestionar_empleados()

    # EDITAR EMPLEADO
    def editar_empleado(self, datos):
        """
        Edita los datos de un empleado existente.

        - Recibe los datos actuales desde la vista
        - Muestra formulario de edición
        - Actualiza la base de datos
        - Retorna el empleado actualizado para refrescar la tabla
        """
        # Convertir los datos recibidos en un diccionario
        datos_empleado = {
            "id_cliente": datos[0],
            "nombre": datos[1],
            "telefono": datos[2],
            "notas": datos[3]
        }

        # Mostrar formulario de edición con datos actuales
        datos_actualizados = ventana_emergente.editar_datos_empleado(datos_empleado)

        # Si el usuario cancela o no completa los datos
        if not datos_actualizados:
            ventana_emergente.mostrar_advertencia(
                "Sin datos",
                "Debe completar los datos para editar el empleado."
            )
            return None

        # Actualizar los datos del empleado en la base de datos
        Cliente.actualizar_empleado(
            datos_actualizados["id_cliente"],
            datos_actualizados["nombre"],
            datos_actualizados["telefono"],
            datos_actualizados["notas"]
        )

        # Confirmación visual
        ventana_emergente.mostrar_informacion(
            "Éxito",
            f"Empleado {datos_actualizados['nombre']} actualizado correctamente."
        )

        # Refrescamos panel de gestion de empleados
        self.gestionar_empleados()

    # ELIMINAR EMPLEADO
    def eliminar_empleado(self, datos):
        """
        Elimina un empleado del sistema.

        - Solicita confirmación al usuario
        - Elimina el registro de la base de datos
        - Retorna el ID eliminado para actualizar la tabla
        """
        # Confirmar la eliminación del empleado
        empleado_eliminado = ventana_emergente.confirmar(
            "Eliminar!",
            f"¿Está seguro de eliminar al empleado {datos[1]}?"
        )

        print(datos)

        # Si el usuario cancela la acción
        if empleado_eliminado is False:
            ventana_emergente.mostrar_error(
                "No eliminado!",
                f"El empleado {datos[1]} no fue eliminado!"
            )
            return None

        # Eliminar el empleado de la base de datos
        Cliente.eliminar_empleado(datos[0])

        # Confirmación visual
        ventana_emergente.mostrar_informacion(
            "Empleado eliminado",
            f"El empleado {datos[1]} fue eliminado exitosamente!"
        )

        # Refrescamos panel de gestion de empleados
        self.gestionar_empleados()

    # Crear backup
    def cargar_backup(self):
        """
        Carga el panel de administración de backups del sistema.

        RESPONSABILIDAD:
        -----------------
        - Obtener el correo de destino configurado para los backups
        - Validar que dicho correo exista
        - Inicializar el panel de backups inyectando los callbacks necesarios

        FLUJO:
        ------
        1. Consulta en la base de datos el correo de destino para backups
        2. Si no existe un correo configurado, muestra un error y detiene el flujo
        3. Si existe, carga el panel de backups pasando:
           - Correo actual
           - Callback para cambiar correo
           - Callback para generar backup
           - Callback para regresar al panel anterior

        NOTAS:
        ------
        - Este método NO genera backups
        - Solo orquesta la navegación y validaciones previas
        - La vista no accede a la base de datos
        """

        correo_backup = DatosConfiguracion.obtener_correo_backup()

        if not correo_backup:
            ventana_emergente.mostrar_error(
                "Error!",
                "No se ha configurado un correo de destino para los backups."
            )
            return

        self.ventana.set_panel_administrador_backup(
            correo_backup,
            self.cambiar_correo_backup,
            self.generar_backup,
            self.regresar_inicio
        )


    #Metodo para cambiar correo de backup
    def cambiar_correo_backup(self):
        """
        Permite cambiar el correo de destino donde se enviarán los backups.

        RESPONSABILIDAD:
        -----------------
        - Solicitar al usuario un nuevo correo de destino
        - Validar que se haya ingresado información
        - Actualizar el correo en la base de datos
        - Notificar el resultado al usuario

        FLUJO:
        ------
        1. Solicita al usuario el nuevo correo mediante una ventana emergente
        2. Si el usuario cancela o no ingresa datos, muestra un error
        3. Si el correo es válido:
           - Se guarda en la base de datos
           - Se muestra un mensaje de éxito

        NOTAS:
        ------
        - El correo se guarda en BD, no en el .env
        - Permite modificar el destino sin reiniciar la aplicación
        """
        nuevo_correo = ventana_emergente.pedir_texto("Cambiar correo de backup", "Ingrese el nuevo correo destino para los backups:")

        if not nuevo_correo:
            ventana_emergente.mostrar_error("Error!", "Debe ingresar un correo válido.")
            return 

        DatosConfiguracion.cambiar_correo_backup(nuevo_correo)
        ventana_emergente.mostrar_informacion("Éxito!", "Correo de backup actualizado correctamente.")

    #Metodo para generar backup
    def generar_backup(self, fecha_inicio, fecha_fin):
        """
        Genera un backup intencional del sistema y lo envía por correo electrónico.

        RESPONSABILIDAD:
        -----------------
        - Generar archivos Excel con información del sistema
        - Construir el mensaje HTML del correo
        - Enviar el correo con los archivos adjuntos
        - Notificar al usuario el resultado del proceso

        PARÁMETROS:
        -----------
        fecha_inicio (str | date):
            Fecha inicial del rango de transacciones a respaldar

        fecha_fin (str | date):
            Fecha final del rango de transacciones a respaldar

        FLUJO:
        ------
        1. Genera un Excel con las transacciones entre las fechas indicadas
        2. Genera un Excel con el listado completo de clientes
        3. Construye un correo en formato HTML con la información del backup
        4. Obtiene el correo de destino desde la base de datos
        5. Envía el correo con ambos archivos adjuntos
        6. Muestra confirmación visual al usuario

        NOTAS:
        ------
        - Este backup es MANUAL (iniciado desde el panel)
        - Es independiente del backup automático diario
        - Los archivos se generan dinámicamente según el rango elegido
        """
        #Generar excel con las fechas acordadas de transacciones
        gt = gestion_archivos()
        ruta_transacciones = gt.guardar_datos_transacciones_excel_por_fecha(fecha_inicio, fecha_fin)

        #Generar excel con todos los clientes
        ruta_clientes = gt.guardar_datos_clientes_excel()

        #Enviar correo con los archivos adjuntos
        mensaje_enviado = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
              <meta charset="UTF-8">
            </head>
            <body style="font-family: Arial; background-color: #f4f6f8; padding: 20px;">
              <div style="max-width:600px; background:#ffffff; margin:auto; border-radius:8px;">
                
                <div style="background:#2c3e50; color:white; padding:20px; text-align:center;">
                  <h2>📦 Backup del Sistema GYIE</h2>
                </div>

                <div style="padding:20px; color:#333;">
                  <p>Se ha generado correctamente un respaldo del sistema.</p>

                  <p><strong>📅 Rango de fechas:</strong></p>
                  <ul>
                    <li>Desde: <strong>{fecha_inicio}</strong></li>
                    <li>Hasta: <strong>{fecha_fin}</strong></li>
                  </ul>

                  <p>Archivos adjuntos:</p>
                  <ul>
                    <li>📊 Transacciones del período</li>
                    <li>👥 Listado completo de clientes</li>
                  </ul>

                  <p>Guarde estos archivos en un lugar seguro.</p>
                </div>

                <div style="background:#ecf0f1; text-align:center; padding:10px; font-size:12px;">
                  © {datetime.now().year} Yalejo · Sistema GYIE<br>
                  Este correo fue generado automáticamente.
                </div>

              </div>
            </body>
            </html>
            """

        #Enviar correo
        correo_destino = DatosConfiguracion.obtener_correo_backup()
        enviador_mensajes.enviar_mensaje_html_con_archivos(correo_destino, "📦 Backup intencional del sistema GYIE", mensaje_enviado, [ruta_transacciones, ruta_clientes])

        ventana_emergente.mostrar_informacion("Éxito!", f"Backup enviado correctamente al correo {correo_destino}.")   

    #Importar desde excel
    def importar_excel(self):
        """
        Importa información al sistema desde un archivo Excel seleccionado por el usuario.

        RESPONSABILIDAD:
        -----------------
        - Solicitar al usuario la selección de un archivo Excel
        - Validar que el archivo seleccionado sea un backup válido
        - Determinar el tipo de información a importar (clientes o transacciones)
        - Ejecutar la lógica de importación correspondiente
        - Notificar al usuario el resultado del proceso

        PARÁMETROS:
        -----------
        Ninguno

        FLUJO:
        ------
        1. Abre un selector de archivos para elegir un Excel
        2. Valida que el archivo seleccionado exista y sea válido
        3. Identifica el tipo de backup según el nombre del archivo
        4. Importa los datos faltantes en la base de datos
        5. Muestra un mensaje de éxito o error según el resultado

        NOTAS:
        ------
        - Solo se aceptan archivos generados por el sistema
        - No sobrescribe registros existentes, solo importa faltantes
        - Los archivos válidos son:
          * clientes.xlsx
          * transacciones_por_fecha_*.xlsx
        """
        ruta = ventana_emergente.seleccionar_archivo()

        if not ruta:
            ventana_emergente.mostrar_error("Error!", "Debe seleccionar un archivo Excel válido.")
            return
        
        nombre_archivo = os.path.basename(ruta)

        if nombre_archivo == "clientes.xlsx":
            #Logica de importacion de backup cliente
            gt = gestion_archivos()
            gt.importar_clientes(ruta)
            ventana_emergente.mostrar_informacion("Éxito!", "Se importaron con exito todos los registros faltantes de clientes.")
        elif nombre_archivo.startswith("transacciones_por_fecha") and nombre_archivo.endswith(".xlsx"):
            #Logica de importacion de backup transacciones
            gt = gestion_archivos()
            gt.importar_transacciones(ruta)
            ventana_emergente.mostrar_informacion("Éxito!", "Se importaron con exito todos los registros faltantes de transacciones.")
        else:
            ventana_emergente.mostrar_error("Error!", "El archivo seleccionado no es un backup válido.")
            return

    #Cambiar contraseña admin
    def cambiar_contraseña_admin(self):
        """
        Permite cambiar la contraseña del administrador del sistema.

        RESPONSABILIDAD:
        -----------------
        - Solicitar la nueva contraseña de administrador
        - Solicitar confirmación de la contraseña ingresada
        - Validar que ambas contraseñas coincidan
        - Actualizar la contraseña en la base de datos
        - Informar al usuario el resultado de la operación

        PARÁMETROS:
        -----------
        Ninguno

        FLUJO:
        ------
        1. Solicita al usuario la nueva contraseña
        2. Solicita la confirmación de la contraseña
        3. Valida que ambas contraseñas sean iguales
        4. Guarda la nueva contraseña en la base de datos
        5. Muestra un mensaje de éxito o error

        NOTAS:
        ------
        - La contraseña se almacena a través de la configuración del sistema
        - La operación es manual y solo accesible desde el panel de administración
        - Si las contraseñas no coinciden, el proceso se cancela
        """
        contraseña_nueva = ventana_emergente.pedir_contraseña("Cambiar Contraseña de Administrador", "Ingrese la nueva contraseña de administrador:")

        confirmacion_contraseña_nueva = ventana_emergente.pedir_contraseña("Confirmar Contraseña", "Confirme la nueva contraseña de administrador:")

        if not contraseña_nueva or not confirmacion_contraseña_nueva:
            ventana_emergente.mostrar_error("Error!", "Debe ingresar y confirmar la nueva contraseña.")
            return
        
        if contraseña_nueva == confirmacion_contraseña_nueva:
            DatosConfiguracion.cambiar_contraseña(contraseña_nueva)

            ventana_emergente.mostrar_informacion("Éxito!", "Contraseña de administrador cambiada correctamente.")  
        else:
            ventana_emergente.mostrar_error("Error!", "Las contraseñas no coinciden. Intente nuevamente.")
            return
        
# Ver estadísticas del sistema
    def ver_estadisticas(self):
        """
        Muestra el panel de estadísticas del sistema.

        RESPONSABILIDAD:
        -----------------
        - Obtener la información estadística desde la capa de datos
        - Enviar los datos necesarios a la vista de estadísticas
        - Cambiar el panel actual por el panel de estadísticas
        - Definir la acción para regresar al panel principal

        PARÁMETROS:
        -----------
        Ninguno

        FUENTES DE DATOS:
        -----------------
        - clientes_mayor_deuda    : Clientes con mayor monto de deuda pendiente
        - deuda_vs_abono          : Total acumulado histórico de deudas frente a abonos
        - deudas_antiguas         : Deudas pendientes más antiguas con días transcurridos
        - transacciones_por_mes   : Resumen mensual de deudas y abonos
        - resumen_hoy             : KPIs del día actual (caja, nequi, deudas nuevas, pagadas)
        - rendimiento_empleados   : Cuánto fió cada empleado y qué porcentaje se recuperó
        - flujo_semanal           : Entradas vs deudas nuevas de los últimos 7 días
        - clientes_riesgosos      : Clientes con deuda antigua sin ningún pago reciente

        FLUJO:
        ------
        1. Solicita a la capa de datos la información estadística necesaria
        2. Envía los datos al panel de estadísticas
        3. Cambia la vista actual a la vista de estadísticas
        4. Define el método de regreso al panel principal

        NOTAS:
        ------
        - Este método NO procesa datos, solo los coordina
        - Sigue el patrón MVC:
          * Modelo: datos_graficas
          * Vista: panel_administrador_estadisticas
          * Controlador: este método
        - Todas las consultas se realizan antes de mostrar la vista
        """
        self.ventana.set_panel_administrador_estadisticas(
            clientes_mayor_deuda=datos_graficas.obtener_clientes_con_mayor_deuda(),
            deuda_vs_abono=datos_graficas.obtener_total_deudas_y_abonos(),
            deudas_antiguas=datos_graficas.obtener_lista_deudas_mas_antiguas(),
            transacciones_por_mes=datos_graficas.obtener_transacciones_por_mes(),
            resumen_hoy=datos_graficas.obtener_resumen_hoy(),
            rendimiento_empleados=datos_graficas.obtener_rendimiento_por_empleado(),
            flujo_semanal=datos_graficas.obtener_flujo_semanal(),
            clientes_riesgosos=datos_graficas.obtener_clientes_riesgosos(),
            on_regresar=self.regresar_inicio
        )