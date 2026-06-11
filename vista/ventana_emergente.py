import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog

from modelo.cliente import Cliente 

class ventana_emergente:

    # ============================
    #  MENSAJES BÁSICOS
    # ============================

    @staticmethod
    def mostrar_informacion(titulo, mensaje):
        messagebox.showinfo(titulo, mensaje)

    @staticmethod
    def mostrar_advertencia(titulo, mensaje):
        messagebox.showwarning(titulo, mensaje)

    @staticmethod
    def mostrar_error(titulo, mensaje):
        messagebox.showerror(titulo, mensaje)

    @staticmethod
    def preguntar_confirmacion(titulo, mensaje):
        return messagebox.askyesno(titulo, mensaje)

    @staticmethod
    def confirmar(titulo, mensaje):
        return messagebox.askyesno(titulo, mensaje)
    
    @staticmethod
    def pedir_texto(titulo, mensaje):
        return simpledialog.askstring(titulo, mensaje)

    @staticmethod
    def pedir_contraseña(titulo, mensaje):
        return simpledialog.askstring(titulo, mensaje, show='#')

    @staticmethod
    def pedir_entero(titulo, mensaje):
        return simpledialog.askinteger(titulo, mensaje)

    @staticmethod
    def pedir_decimal(titulo, mensaje):
        return simpledialog.askfloat(titulo, mensaje)

    @staticmethod
    def mostrar_informacion_transaccion(titulo, mensaje):
        ventana = tk.Toplevel()
        ventana.title(titulo)
        ventana.geometry("400x300")

        lbl = tk.Label(
            ventana,
            text=mensaje,
            justify="left",
            anchor="nw"
        )
        lbl.pack(fill="both", expand=True, padx=15, pady=15)

        btn = tk.Button(ventana, text="Cerrar", command=ventana.destroy)
        btn.pack(pady=(0, 10))

    
    @staticmethod
    def seleccionar_archivo(titulo="Seleccionar archivo", tipos_archivo=None):
        """
        Muestra un diálogo para seleccionar un archivo del sistema.

        Args:
            titulo (str): Título de la ventana.
            tipos_archivo (list): Lista de tuplas con tipos de archivo.
                Ejemplo:
                [("Archivos Excel", "*.xlsx"), ("Todos", "*.*")]

        Returns:
            str | None: Ruta completa del archivo seleccionado o None si se cancela.
        """

        ruta = filedialog.askopenfilename(
            title=titulo,
            filetypes=tipos_archivo if tipos_archivo else [("Todos los archivos", "*.*")]
        )

        if not ruta:
            return None

        return ruta


    # ============================
    #  SELECCIONAR ELEMENTO
    # ============================
    @staticmethod
    def seleccionar_de_lista(titulo, mensaje, lista):
        if not lista:
            return None

        ventana = tk.Toplevel()
        ventana.title(titulo)
        ventana.geometry("350x190")
        ventana.resizable(False, False)

        ventana.grab_set()
        ventana.focus()

        tk.Label(ventana, text=mensaje, font=("Arial", 12)).pack(pady=10)

        if isinstance(lista[0], dict):
            valores = [item["nombre"] for item in lista]
        else:
            valores = lista

        combo = ttk.Combobox(
            ventana,
            values=valores,
            state="readonly",
            font=("Arial", 11),
            width=25
        )
        combo.pack(pady=5)
        combo.current(0)

        seleccionado = {"valor": None}

        def aceptar():
            idx = combo.current()
            seleccionado["valor"] = lista[idx]
            ventana.destroy()

        def cancelar():
            ventana.destroy()

        frame = tk.Frame(ventana)
        frame.pack(pady=10)

        tk.Button(frame, text="Aceptar", width=10, command=aceptar).pack(side="left", padx=5)
        tk.Button(frame, text="Cancelar", width=10, command=cancelar).pack(side="left", padx=5)

        ventana.wait_window()
        return seleccionado["valor"]


    # ============================
    #  PEDIR DATOS TRANSACCIÓN
    # ============================
    @staticmethod
    def pedir_datos_transaccion(titulo, tipo, clientes, on_agregar_cliente):
        ventana = tk.Toplevel()
        ventana.title(titulo)
        ventana.geometry("440x400")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.focus()

        resultado = {"datos": None}

        # ========== CLIENTE CON BÚSQUEDA ==========
        tk.Label(ventana, text="Cliente:", font=("Arial", 11)).pack(pady=(10, 0))

        frame_cliente = tk.Frame(ventana)
        frame_cliente.pack(pady=5)

        # variable que guarda el id_cliente seleccionado actualmente
        cliente_seleccionado = {"id": None, "nombre": ""}

        # Entry de búsqueda
        var_busqueda = tk.StringVar()
        entry_cliente = tk.Entry(
            frame_cliente,
            textvariable=var_busqueda,
            width=24,
            font=("Arial", 11)
        )
        entry_cliente.pack(side="left", padx=5)

        # ---- Lista desplegable flotante ----
        listbox_frame = tk.Frame(ventana, relief="solid", bd=1)
        listbox_var   = tk.Listbox(
            listbox_frame,
            height=5,
            font=("Arial", 10),
            activestyle="dotbox",
            selectmode="single"
        )
        scrollbar_lb  = tk.Scrollbar(listbox_frame, orient="vertical", command=listbox_var.yview)
        listbox_var.configure(yscrollcommand=scrollbar_lb.set)
        scrollbar_lb.pack(side="right", fill="y")
        listbox_var.pack(side="left", fill="both", expand=True)
        # el frame flotante se posicionará dinámicamente; empieza oculto
        listbox_frame.place_forget()

        def _mostrar_lista():
            # posicionar debajo del entry_cliente
            entry_cliente.update_idletasks()
            x = entry_cliente.winfo_rootx() - ventana.winfo_rootx()
            y = entry_cliente.winfo_rooty() - ventana.winfo_rooty() + entry_cliente.winfo_height()
            listbox_frame.place(x=x, y=y, width=entry_cliente.winfo_width() + 4)
            listbox_frame.lift()

        def _ocultar_lista():
            listbox_frame.place_forget()

        def _filtrar(*_):
            texto = var_busqueda.get().strip().lower()
            listbox_var.delete(0, "end")

            # si el texto coincide exactamente con el seleccionado, no abrir lista
            if texto == cliente_seleccionado["nombre"].lower():
                _ocultar_lista()
                return

            coincidencias = [
                c for c in clientes
                if texto in c["nombre"].lower()
            ]

            if not coincidencias or texto == "":
                # mostrar todos cuando está vacío
                coincidencias = clientes

            for c in coincidencias:
                listbox_var.insert("end", c["nombre"])

            # guardar referencia para recuperar id al seleccionar
            listbox_var._clientes_filtrados = coincidencias

            _mostrar_lista()

        def _seleccionar_de_lista(event=None):
            idx = listbox_var.curselection()
            if not idx:
                return
            seleccion = listbox_var._clientes_filtrados[idx[0]]
            cliente_seleccionado["id"]     = seleccion["id_cliente"]
            cliente_seleccionado["nombre"] = seleccion["nombre"]
            var_busqueda.set(seleccion["nombre"])
            _ocultar_lista()
            # mover foco al siguiente campo
            combo_subtipo.focus()

        listbox_var.bind("<<ListboxSelect>>", _seleccionar_de_lista)
        listbox_var.bind("<Return>",           _seleccionar_de_lista)
        var_busqueda.trace_add("write", _filtrar)

        # abrir lista al hacer foco en el entry
        entry_cliente.bind("<FocusIn>",  lambda e: _filtrar())
        # cerrar lista al presionar Escape
        entry_cliente.bind("<Escape>",   lambda e: _ocultar_lista())
        # navegar con teclado desde el entry hacia la lista
        def _bajar_a_lista(event):
            if listbox_var.size() > 0:
                listbox_var.focus()
                listbox_var.selection_set(0)
        entry_cliente.bind("<Down>", _bajar_a_lista)
        # volver al entry desde la lista con Escape
        listbox_var.bind("<Escape>", lambda e: (entry_cliente.focus(), _ocultar_lista()))

        # inicializar con el primer cliente
        if clientes:
            cliente_seleccionado["id"]     = clientes[0]["id_cliente"]
            cliente_seleccionado["nombre"] = clientes[0]["nombre"]
            var_busqueda.set(clientes[0]["nombre"])

        # ------ REFRESCAR CLIENTES ------
        def refrescar_clientes():
            nuevos_clientes = Cliente.obtener_todos()
            clientes.clear()
            clientes.extend(nuevos_clientes)

            if nuevos_clientes:
                ultimo = nuevos_clientes[-1]
                cliente_seleccionado["id"]     = ultimo["id_cliente"]
                cliente_seleccionado["nombre"] = ultimo["nombre"]
                var_busqueda.set(ultimo["nombre"])

        # ------ AGREGAR CLIENTE + REFRESCAR ------
        def agregar_cliente_y_refrescar():
            datos = on_agregar_cliente()
            if datos:
                refrescar_clientes()

        btn_agregar_cliente = tk.Button(
            frame_cliente,
            text="+ Cliente",
            width=10,
            command=agregar_cliente_y_refrescar
        )
        btn_agregar_cliente.pack(side="left", padx=5)

        # ========== SUBTIPO ==========
        tk.Label(ventana, text="Subtipo:", font=("Arial", 11)).pack(pady=(10, 0))

        if tipo == "ABONO":
            opciones_subtipo = ["PAGO_DEUDA", "NEQUI_RECIBIDO", "OTROS_INGRESOS"]
        else:
            opciones_subtipo = ["FIADO", "PRESTAMO", "NEQUI_PENDIENTE"]

        combo_subtipo = ttk.Combobox(
            ventana,
            values=opciones_subtipo,
            state="readonly",
            width=30
        )
        combo_subtipo.pack(pady=5)
        combo_subtipo.current(0)

        # ========== MONTO ==========
        tk.Label(ventana, text="Monto:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_monto = tk.Entry(ventana, width=30)
        entry_monto.pack(pady=5)

        # ========== DESCRIPCIÓN ==========
        tk.Label(ventana, text="Descripción:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_descripcion = tk.Entry(ventana, width=30)
        entry_descripcion.pack(pady=5)

        # ========== BOTONES ==========
        frame_botones = tk.Frame(ventana)
        frame_botones.pack(pady=15)

        def guardar():
            # cerrar lista si está abierta
            _ocultar_lista()

            if cliente_seleccionado["id"] is None:
                messagebox.showerror("Error", "Debe seleccionar un cliente válido de la lista.")
                return

            try:
                monto = float(entry_monto.get())
                if monto <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Error", "Ingrese un monto válido mayor a 0.")
                return

            subtipo     = combo_subtipo.get()
            descripcion = entry_descripcion.get()

            resultado["datos"] = {
                "id_cliente":  cliente_seleccionado["id"],
                "monto":       monto,
                "subtipo":     subtipo,
                "descripcion": descripcion
            }

            ventana.destroy()

        def cancelar():
            ventana.destroy()

        tk.Button(frame_botones, text="Guardar",  width=12, command=guardar).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Cancelar", width=12, command=cancelar).pack(side="left", padx=10)

        ventana.wait_window()
        return resultado["datos"]


    # ============================
    #  PEDIR DATOS CLIENTE
    # ============================
    @staticmethod
    def pedir_datos_cliente():
        ventana = tk.Toplevel()
        ventana.title("Nuevo Cliente")
        ventana.geometry("350x300")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.focus()

        resultado = {"datos": None}

        tk.Label(ventana, text="Nombre:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_nombre = tk.Entry(ventana, width=30)
        entry_nombre.pack(pady=5)

        tk.Label(ventana, text="Teléfono:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_telefono = tk.Entry(ventana, width=30)
        entry_telefono.pack(pady=5)

        tk.Label(ventana, text="Notas / Dirección:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_notas = tk.Entry(ventana, width=30)
        entry_notas.pack(pady=5)

        frame_botones = tk.Frame(ventana)
        frame_botones.pack(pady=20)

        def guardar():
            nombre   = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            notas    = entry_notas.get().strip()

            if nombre == "":
                messagebox.showerror("Error", "El nombre no puede estar vacío.")
                return

            resultado["datos"] = {
                "nombre":   nombre,
                "telefono": telefono,
                "notas":    notas
            }

            ventana.destroy()

        def cancelar():
            ventana.destroy()

        tk.Button(frame_botones, text="Guardar",  width=12, command=guardar).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Cancelar", width=12, command=cancelar).pack(side="left", padx=10)

        ventana.wait_window()
        return resultado["datos"]
    
    # ============================
    #  EDITAR DATOS EMPLEADO
    # ============================
    @staticmethod
    def editar_datos_empleado(datos_empleado):
        if not datos_empleado:
            return None

        ventana = tk.Toplevel()
        ventana.title("Editar Empleado")
        ventana.geometry("350x300")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.focus()

        resultado = {"datos": None}

        # ========== NOMBRE ==========
        tk.Label(ventana, text="Nombre:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_nombre = tk.Entry(ventana, width=30)
        entry_nombre.pack(pady=5)
        entry_nombre.insert(0, datos_empleado["nombre"])

        # ========== TELÉFONO ==========
        tk.Label(ventana, text="Teléfono:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_telefono = tk.Entry(ventana, width=30)
        entry_telefono.pack(pady=5)
        entry_telefono.insert(0, datos_empleado["telefono"])

        # ========== NOTAS ==========
        tk.Label(ventana, text="Notas / Dirección:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_notas = tk.Entry(ventana, width=30)
        entry_notas.pack(pady=5)
        entry_notas.insert(0, datos_empleado["notas"])

        # ========== BOTONES ==========
        frame_botones = tk.Frame(ventana)
        frame_botones.pack(pady=20)

        def guardar():
            nombre   = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            notas    = entry_notas.get().strip()

            if nombre == "":
                messagebox.showerror("Error", "El nombre no puede estar vacío.")
                return

            resultado["datos"] = {
                "id_cliente": datos_empleado["id_cliente"],
                "nombre":     nombre,
                "telefono":   telefono,
                "notas":      notas
            }

            ventana.destroy()

        def cancelar():
            ventana.destroy()

        tk.Button(frame_botones, text="Guardar",  width=12, command=guardar).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Cancelar", width=12, command=cancelar).pack(side="left", padx=10)

        ventana.wait_window()
        return resultado["datos"]