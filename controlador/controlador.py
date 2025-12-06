from vista.ventana import Ventana
from vista.ventana_emergente import ventana_emergente

from modelo.cliente import Cliente
from modelo.transaccion import Transaccion
from modelo.filtros import Filtros

from datetime import datetime

class Controller:

    def __init__(self):
        self.ventana = Ventana()
        self.empleado_en_turno = None
        self.id_empleado_en_turno = None
        self.ventana.set_on_click_transaccion(self.mostrar_detalles_transaccion)

    def iniciar(self):
        self.ventana.set_panel_inicio(
            on_admin=self.login_admin,
            on_empleado=self.login_empleado
        )
        self.ventana.mainloop()
    
    #Metodo para cargar el deshboard al inicar la aplicacion
    def recargar_dashboard(self):
        transacciones = Transaccion.obtener_todas()

        datos_tabla = []
        total_deuda = 0
        total_abonos = 0

        for transaccion in transacciones:

            nombre = Cliente.obtener_nombre_por_id(transaccion['id_cliente'])
            fecha = transaccion['fecha_creacion'].strftime("%Y-%m-%d-%H:%M:%S")
            tipo = transaccion['tipo_transaccion']
            monto = float(transaccion['monto'])

            if tipo == "DEUDA":
                debe = monto
                abono = 0
                total_deuda += monto
            else:
                debe = 0
                abono = monto
                total_abonos += monto

            datos_tabla.append((transaccion["id_transaccion"], nombre, debe, abono, fecha, "Ver"))

        self.ventana.set_panel_dashboard(
            datos_tabla,
            total_deuda,
            total_abonos,
            on_nuevo_abono=self.registrar_nuevo_abono,
            on_nueva_deuda=self.registrar_nueva_deuda,
            on_filtrar=self.aplicar_filtros
        )

    #Metodo para actualizar dasboard usando filtros
    def _filtrar_dashboard(self, transacciones):
        datos_tabla = []
        total_deuda = 0
        total_abonos = 0

        for transaccion in transacciones:
            nombre = Cliente.obtener_nombre_por_id(transaccion['id_cliente'])
            fecha = transaccion['fecha_creacion'].strftime("%Y-%m-%d-%H:%M:%S")
            tipo = transaccion['tipo_transaccion']
            monto = float(transaccion['monto'])

            if tipo == "DEUDA":
                debe = monto
                abono = 0
                total_deuda += monto
            else:
                debe = 0
                abono = monto
                total_abonos += monto

            datos_tabla.append((transaccion["id_transaccion"], nombre, debe, abono, fecha, "Ver"))

        self.ventana.set_panel_dashboard(
            datos_tabla,
            total_deuda,
            total_abonos,
            self.registrar_nuevo_abono,
            self.registrar_nueva_deuda,
            self.aplicar_filtros
        )

    def login_admin(self):
        print("Login como Admin")

    def login_empleado(self):
        empleados = Cliente.obtener_empleados()

        empleado = ventana_emergente.seleccionar_de_lista("Selección de Empleado", "Seleccione su nombre de la lista:" ,empleados)

        if empleado is None:
            ventana_emergente.mostrar_advertencia("Selección Cancelada", "No se seleccionó ningún empleado.")
            return

        self.empleado_en_turno = empleado
        self.id_empleado_en_turno = empleado['id_cliente']

        ventana_emergente.mostrar_informacion("Bienvenido", f"Has iniciado sesión como {empleado['nombre']}.")

        self.recargar_dashboard()

    #Metodo para registrar un nuevo abono
    def registrar_nuevo_abono(self):

        clientes = Cliente.obtener_todos()

        datos = ventana_emergente.pedir_datos_transaccion(
            "Nuevo Abono",
            "ABONO",
            clientes
        )

        if datos is None:
            return

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
    
    #Metodo para registrar una nueva deuda
    def registrar_nueva_deuda(self):

        clientes = Cliente.obtener_todos()

        datos = ventana_emergente.pedir_datos_transaccion(
            "Nueva Deuda",
            "DEUDA",
            clientes
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

    def aplicar_filtros(self, filtros):

        transacciones = Transaccion.obtener_todas()

        #Filtro por fecha
        if filtros["fecha"]:
            resultado_fecha = Filtros.filtrar_por_fecha(filtros["fecha"])
            ids_fecha = {t["id_transaccion"] for t in resultado_fecha}

            transacciones = [
                t for t in transacciones 
                if t["id_transaccion"] in ids_fecha
            ]

        #Filtro por nombre
        if filtros["nombre"]:
            resultado_nombre = Filtros.filtrar_por_nombre_cliente(filtros["nombre"])
            ids_nombre = {t["id_transaccion"] for t in resultado_nombre}

            transacciones = [
                t for t in transacciones 
                if t["id_transaccion"] in ids_nombre
            ]

        #Filtro por estado
        if filtros["estado"]:
            resultado_estado = Filtros.filtrar_por_estado_deuda(filtros["estado"])
            ids_estado = {t["id_transaccion"] for t in resultado_estado}

            transacciones = [
                t for t in transacciones 
                if t["id_transaccion"] in ids_estado
            ]

        #Filtro por orden
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

        #Actualizar dashboard
        self._filtrar_dashboard(transacciones)

    #metodo para mostrar la informacion de la fila seleccionada
    def mostrar_detalles_transaccion(self, valores):
        #Marcamos variables traidas desde la tabla principal.
        id, cliente, deuda, abono, fecha, _ = valores

        #Consultamos informacion sobre la transaccion y el cliente.
        datos_transaccion = Transaccion.obtener_por_id(id)
        datos_cliente = Cliente.obtener_por_id(datos_transaccion["id_cliente"])
        
        #Convertimos infoirmacion de la tabla (deuda o bono) a floats.
        deuda = float(deuda)
        abono = float(abono)

        #En un string ponemos toda la informacion que queremos mostrar en una ventana emergente
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

        #Mostramos en la ventana la informacion
        ventana_emergente.mostrar_informacion_transaccion("Datos transaccion", datos)