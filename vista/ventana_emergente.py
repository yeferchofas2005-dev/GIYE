import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

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
        ventana.geometry("420x360")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.focus()

        resultado = {"datos": None}

        # ========== CLIENTE ==========
        tk.Label(ventana, text="Cliente:", font=("Arial", 11)).pack(pady=(10, 0))

        frame_cliente = tk.Frame(ventana)
        frame_cliente.pack(pady=5)

        valores_clientes = [c["nombre"] for c in clientes]

        combo_cliente = ttk.Combobox(
            frame_cliente,
            values=valores_clientes,
            state="readonly",
            width=22
        )
        combo_cliente.pack(side="left", padx=5)
        combo_cliente.current(0)

        # ------ REFRESCAR CLIENTES ------
        def refrescar_clientes():  # evitar import cíclico
            nuevos_clientes = Cliente.obtener_todos()
            nuevos_nombres = [c["nombre"] for c in nuevos_clientes]

            combo_cliente["values"] = nuevos_nombres
            combo_cliente.current(len(nuevos_nombres) - 1)

            clientes.clear()
            clientes.extend(nuevos_clientes)

        # ------ AGREGAR CLIENTE + REFRESCAR ------
        def agregar_cliente_y_refrescar():
            datos = on_agregar_cliente()  # Llama al controlador
            if datos:
                refrescar_clientes()

        btn_agregar_cliente = tk.Button(
            frame_cliente,
            text="Agregar Cliente",
            width=15,
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
        frame_botones.pack(pady=20)

        def guardar():
            try:
                cliente_idx = combo_cliente.current()
                id_cliente = clientes[cliente_idx]["id_cliente"]

                monto = float(entry_monto.get())
                subtipo = combo_subtipo.get()
                descripcion = entry_descripcion.get()

                if monto <= 0:
                    raise ValueError

                resultado["datos"] = {
                    "id_cliente": id_cliente,
                    "monto": monto,
                    "subtipo": subtipo,
                    "descripcion": descripcion
                }

                ventana.destroy()

            except:
                messagebox.showerror("Error", "Datos inválidos. Verifique el monto.")

        def cancelar():
            ventana.destroy()

        tk.Button(frame_botones, text="Guardar", width=12, command=guardar).pack(side="left", padx=10)
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
            nombre = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            notas = entry_notas.get().strip()

            if nombre == "":
                messagebox.showerror("Error", "El nombre no puede estar vacío.")
                return

            resultado["datos"] = {
                "nombre": nombre,
                "telefono": telefono,
                "notas": notas
            }

            ventana.destroy()

        def cancelar():
            ventana.destroy()

        tk.Button(frame_botones, text="Guardar", width=12, command=guardar).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Cancelar", width=12, command=cancelar).pack(side="left", padx=10)

        ventana.wait_window()
        return resultado["datos"]
