import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

class ventana_emergente:

#Metodos estatico donde se usa MessageBox para mostrar mensajes emergentes

#Metodos de ventanas emergentes basicos
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
    def confirmar(titulo, mensaje):
        return messagebox.askyesno(titulo, mensaje)

    @staticmethod
    def pedir_texto(titulo, mensaje):
        return simpledialog.askstring(titulo, mensaje)

    @staticmethod
    def pedir_entero(titulo, mensaje):
        return simpledialog.askinteger(titulo, mensaje)

    @staticmethod
    def pedir_decimal(titulo, mensaje):
        return simpledialog.askfloat(titulo, mensaje)

#Metodo para seleccionar de una lista
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

        tk.Label(
            ventana, text=mensaje, font=("Arial", 12)
        ).pack(pady=10)

        # Mostrar nombres si viene una lista de diccionarios
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

        #Boton de aceptar y cancelar para el metodo de seleccionar de lista
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
    
#Metodo para pedir informacion para la creacion de transacciones
    @staticmethod
    def pedir_datos_transaccion(titulo, tipo, clientes):
        ventana = tk.Toplevel()
        ventana.title(titulo)
        ventana.geometry("420x360")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.focus()

        resultado = {"datos": None}

        # =========================
        # CLIENTE
        # =========================
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

        # Boton para agregar cliente
        btn_agregar_cliente = tk.Button(
            frame_cliente,
            text="Agregar Cliente",
            width=15
        )
        btn_agregar_cliente.pack(side="left", padx=5)

        # =========================
        # SUBTIPO (DINÁMICO)
        # =========================
        tk.Label(ventana, text="Subtipo:", font=("Arial", 11)).pack(pady=(10, 0))

        if tipo == "ABONO":
            opciones_subtipo = ["PAGO_DEUDA", "NEQUI_RECIBIDO", "OTROS_INGRESOS"]
        else:  # DEUDA
            opciones_subtipo = ["FIADO", "PRESTAMO", "NEQUI_PENDIENTE"]

        combo_subtipo = ttk.Combobox(
            ventana,
            values=opciones_subtipo,
            state="readonly",
            width=30
        )
        combo_subtipo.pack(pady=5)
        combo_subtipo.current(0)

        # =========================
        # MONTO
        # =========================
        tk.Label(ventana, text="Monto:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_monto = tk.Entry(ventana, width=30)
        entry_monto.pack(pady=5)

        # =========================
        # DESCRIPCIÓN
        # =========================
        tk.Label(ventana, text="Descripción:", font=("Arial", 11)).pack(pady=(10, 0))
        entry_descripcion = tk.Entry(ventana, width=30)
        entry_descripcion.pack(pady=5)

        # =========================
        # BOTONES
        # =========================
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




