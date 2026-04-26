import tkinter as tk
from tkinter import ttk, messagebox
from models.modelos import Producto, Movimiento

class VentanaMovimientos:
    def __init__(self, container):
        self.container = container
        self.bg_color  = "#F4F6F9"

        for widget in self.container.winfo_children():
            widget.destroy()

        self.tipo_operacion  = tk.StringVar(value="ENTRADA")
        self.productos_data  = []   # Cache completo
        self.productos_filtro = []  # Cache filtrado actual

        self._configurar_estilos()
        self._construir_interfaz()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white",
                        rowheight=35, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#E2E8F0",
                        font=("Segoe UI", 10, "bold"), borderwidth=0)

    def _construir_interfaz(self):
        # HEADER
        header = tk.Frame(self.container, bg=self.bg_color)
        header.pack(fill="x", padx=40, pady=(30, 10))
        tk.Label(header, text="Movimientos de Stock",
                 font=("Segoe UI", 24, "bold"), bg=self.bg_color, fg="#111827").pack(anchor="w")
        tk.Label(header, text="Registra entradas (compras) y salidas (ventas/mermas).",
                 font=("Segoe UI", 11), bg=self.bg_color, fg="#64748B").pack(anchor="w")

        # CAJA DE REGISTRO
        registro_frame = tk.Frame(self.container, bg="white", bd=1,
                                  relief="solid", padx=30, pady=20)
        registro_frame.pack(fill="x", padx=40, pady=(10, 20))

        # Toggle ENTRADA / SALIDA
        lbl_tipo = tk.Label(registro_frame, text="Tipo de Operación", bg="white",
                            font=("Segoe UI", 10, "bold"), fg="#475569")
        lbl_tipo.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.btn_entrada = tk.Button(registro_frame, text="↓\nENTRADA",
                                     font=("Segoe UI", 11, "bold"), width=12, height=4,
                                     cursor="hand2", command=lambda: self.cambiar_tipo("ENTRADA"))
        self.btn_entrada.grid(row=1, column=0, padx=(0, 10))

        self.btn_salida = tk.Button(registro_frame, text="↑\nSALIDA",
                                    font=("Segoe UI", 11, "bold"), width=12, height=4,
                                    cursor="hand2", command=lambda: self.cambiar_tipo("SALIDA"))
        self.btn_salida.grid(row=1, column=1, padx=(0, 20))

        # Formulario
        form_frame = tk.Frame(registro_frame, bg="white")
        form_frame.grid(row=1, column=2, sticky="nw")

        # ── BUSCADOR DE PRODUCTO ────────────────────────────────────────
        tk.Label(form_frame, text="Buscar Producto", bg="white",
                 font=("Segoe UI", 10, "bold"), fg="#475569").grid(
                 row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        buscar_frame = tk.Frame(form_frame, bg="white", highlightbackground="#E2E8F0",
                                highlightthickness=1)
        buscar_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 4))

        tk.Label(buscar_frame, text="🔍", bg="white",
                 font=("Segoe UI", 11)).pack(side="left", padx=(8, 4))
        self.en_buscar = tk.Entry(buscar_frame, font=("Segoe UI", 11),
                                  bd=0, relief="flat", fg="#94A3B8", width=43)
        self.en_buscar.insert(0, "Escribe para filtrar productos...")
        self.en_buscar.pack(side="left", ipady=6, padx=(0, 8))
        self.en_buscar.bind("<FocusIn>",  self._buscar_focus_in)
        self.en_buscar.bind("<FocusOut>", self._buscar_focus_out)
        self.en_buscar.bind("<KeyRelease>", self._filtrar_productos)

        # Lista desplegable de resultados
        self.lista_frame = tk.Frame(form_frame, bg="white", bd=1,
                                    relief="solid")
        self.lista_productos = tk.Listbox(self.lista_frame, font=("Segoe UI", 10),
                                          height=6, bd=0, activestyle="none",
                                          selectbackground="#EEF2FF",
                                          selectforeground="#4361EE")
        self.lista_productos.pack(fill="both", expand=True)
        self.lista_productos.bind("<<ListboxSelect>>", self._seleccionar_de_lista)
        # La lista empieza oculta
        self._lista_visible = False

        # Label de producto seleccionado
        self.lbl_producto_sel = tk.Label(form_frame, text="",
                                          bg="white", fg="#4361EE",
                                          font=("Segoe UI", 10, "bold"))
        self.lbl_producto_sel.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 8))

        # Cantidad y Motivo
        tk.Label(form_frame, text="Cantidad", bg="white",
                 font=("Segoe UI", 10, "bold"), fg="#475569").grid(
                 row=4, column=0, sticky="w", pady=(0, 5))
        self.en_cantidad = tk.Entry(form_frame, font=("Segoe UI", 11),
                                    bg="#F8FAFC", bd=1, relief="solid", width=15)
        self.en_cantidad.grid(row=5, column=0, sticky="w", pady=(0, 10), ipady=5)

        tk.Label(form_frame, text="Motivo (Opcional)", bg="white",
                 font=("Segoe UI", 10, "bold"), fg="#475569").grid(
                 row=4, column=1, sticky="w", pady=(0, 5), padx=(15, 0))
        self.en_motivo = tk.Entry(form_frame, font=("Segoe UI", 11),
                                   bg="#F8FAFC", bd=1, relief="solid", width=28)
        self.en_motivo.grid(row=5, column=1, sticky="w", pady=(0, 10),
                             padx=(15, 0), ipady=5)

        self.btn_guardar = tk.Button(form_frame, text="Registrar Entrada",
                                      command=self.guardar_movimiento,
                                      bg="#10B981", fg="white",
                                      font=("Segoe UI", 11, "bold"),
                                      bd=0, padx=20, pady=8, cursor="hand2")
        self.btn_guardar.grid(row=6, column=0, columnspan=2,
                               sticky="we", pady=(10, 0))

        # FILTROS Y REPORTE
        filtros_frame = tk.Frame(self.container, bg=self.bg_color)
        filtros_frame.pack(fill="x", padx=40, pady=(0, 10))

        tk.Label(filtros_frame, text="📅 Historial General",
                 font=("Segoe UI", 14, "bold"),
                 bg=self.bg_color, fg="#111827").pack(side="left")

        tk.Button(filtros_frame, text="📄 Reporte Kardex",
                  command=self.pedir_kardex,
                  bg="white", fg="#475569", bd=1, relief="solid",
                  font=("Segoe UI", 10), padx=15, pady=5,
                  cursor="hand2").pack(side="right")

        # TABLA HISTORIAL
        table_frame = tk.Frame(self.container, bg="white", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=40, pady=(0, 30))

        columnas = ("Fecha/Hora", "Producto", "Tipo", "Cantidad", "Motivo")
        self.tabla = ttk.Treeview(table_frame, columns=columnas, show="headings")

        anchos = {"Fecha/Hora": 120, "Producto": 250, "Tipo": 80,
                  "Cantidad": 80, "Motivo": 200}
        for col in columnas:
            self.tabla.heading(col, text=col.upper())
            self.tabla.column(col, anchor="center", width=anchos[col])

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tabla.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.tabla.tag_configure("ENTRADA", foreground="#047857", background="#ECFDF5")
        self.tabla.tag_configure("SALIDA",  foreground="#B91C1C", background="#FEF2F2")

        # Inicializar
        self._id_producto_sel = None
        self.cargar_productos()
        self.cargar_historial()
        self.cambiar_tipo("ENTRADA")

    # ──────────────────────────────────────────────────────────────────────
    # BUSCADOR
    # ──────────────────────────────────────────────────────────────────────

    def _buscar_focus_in(self, event):
        if self.en_buscar.get() == "Escribe para filtrar productos...":
            self.en_buscar.delete(0, tk.END)
            self.en_buscar.config(fg="#1E293B")
        self._mostrar_lista()

    def _buscar_focus_out(self, event):
        if self.en_buscar.get().strip() == "":
            self.en_buscar.insert(0, "Escribe para filtrar productos...")
            self.en_buscar.config(fg="#94A3B8")
        # Delay para permitir click en la lista
        self.container.after(200, self._ocultar_lista)

    def _filtrar_productos(self, event=None):
        texto = self.en_buscar.get().strip().lower()
        if texto == "escribe para filtrar productos...":
            texto = ""

        if texto:
            self.productos_filtro = [
                p for p in self.productos_data
                if texto in p["nombre"].lower()
            ]
        else:
            self.productos_filtro = self.productos_data[:]

        self._actualizar_lista()
        self._mostrar_lista()

    def _actualizar_lista(self):
        self.lista_productos.delete(0, tk.END)
        for p in self.productos_filtro:
            estado = "❌" if p["stock"] == 0 else ("⚠️" if p["stock"] <= p["stock_minimo"] else "✅")
            self.lista_productos.insert(
                tk.END,
                f"{estado}  {p['nombre']}  —  Stock: {p['stock']}"
            )

    def _mostrar_lista(self):
        if not self._lista_visible and self.productos_filtro:
            self.lista_frame.grid(row=2, column=0, columnspan=2,
                                  sticky="w", pady=(0, 4))
            self._lista_visible = True

    def _ocultar_lista(self):
        if self._lista_visible:
            self.lista_frame.grid_remove()
            self._lista_visible = False

    def _seleccionar_de_lista(self, event):
        sel = self.lista_productos.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self.productos_filtro):
            prod = self.productos_filtro[idx]
            self._id_producto_sel = prod["id_producto"]
            self.lbl_producto_sel.config(
                text=f"✅  Seleccionado: {prod['nombre']}  |  Stock actual: {prod['stock']}"
            )
            self.en_buscar.delete(0, tk.END)
            self.en_buscar.insert(0, prod["nombre"])
            self.en_buscar.config(fg="#1E293B")
            self._ocultar_lista()

    # ──────────────────────────────────────────────────────────────────────
    # LÓGICA
    # ──────────────────────────────────────────────────────────────────────

    def cambiar_tipo(self, tipo):
        self.tipo_operacion.set(tipo)
        if tipo == "ENTRADA":
            self.btn_entrada.config(bg="#ECFDF5", fg="#047857", relief="solid", bd=2)
            self.btn_salida.config( bg="#F1F5F9", fg="#94A3B8", relief="flat",  bd=0)
            self.btn_guardar.config(text="Registrar Entrada", bg="#10B981")
        else:
            self.btn_salida.config( bg="#FEF2F2", fg="#B91C1C", relief="solid", bd=2)
            self.btn_entrada.config(bg="#F1F5F9", fg="#94A3B8", relief="flat",  bd=0)
            self.btn_guardar.config(text="Registrar Salida", bg="#EF4444")

    def cargar_productos(self):
        self.productos_data   = Producto.obtener_todos()
        self.productos_filtro = self.productos_data[:]
        self._actualizar_lista()

    def cargar_historial(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        for h in Movimiento.obtener_historial():
            tipo = h["tipo_movimiento"]
            self.tabla.insert("", "end", values=(
                h["fecha_hora"], h["producto"],
                tipo, h["cantidad"], h["motivo"]
            ), tags=(tipo,))

    def guardar_movimiento(self):
        if not self._id_producto_sel:
            return messagebox.showerror("Error",
                "Selecciona un producto usando el buscador.")

        cant_texto = self.en_cantidad.get()
        if not cant_texto.isdigit() or int(cant_texto) <= 0:
            return messagebox.showerror("Error",
                "La cantidad debe ser un número mayor a cero.")

        id_prod  = self._id_producto_sel
        tipo     = self.tipo_operacion.get()
        cantidad = int(cant_texto)
        motivo   = self.en_motivo.get() or (
            "Entrada manual" if tipo == "ENTRADA" else "Salida manual"
        )

        # Validar stock suficiente para salidas
        if tipo == "SALIDA":
            prod = next((p for p in self.productos_data
                         if p["id_producto"] == id_prod), None)
            if prod and cantidad > int(prod["stock"]):
                return messagebox.showwarning(
                    "Stock Insuficiente",
                    f"No puedes sacar {cantidad}. Solo hay {prod['stock']} en bodega."
                )

        if Movimiento.registrar(id_prod, tipo, cantidad, motivo):
            messagebox.showinfo("✅ Éxito",
                                f"{tipo.capitalize()} registrada correctamente.")
            self.en_cantidad.delete(0, tk.END)
            self.en_motivo.delete(0, tk.END)
            # Limpiar selección
            self._id_producto_sel = None
            self.lbl_producto_sel.config(text="")
            self.en_buscar.delete(0, tk.END)
            self.en_buscar.insert(0, "Escribe para filtrar productos...")
            self.en_buscar.config(fg="#94A3B8")
            self.cargar_productos()
            self.cargar_historial()
        else:
            messagebox.showerror("Error", "No se pudo registrar el movimiento.")

    # ── KARDEX ────────────────────────────────────────────────────────────

    def pedir_kardex(self):
        """Abre un diálogo para elegir el producto y genera el PDF."""
        win = tk.Toplevel(self.container)
        win.title("Generar Reporte Kardex")
        win.geometry("460x380")
        win.resizable(False, False)
        win.grab_set()
        win.configure(bg="white")

        tk.Label(win, text="📄  Reporte Kardex",
                 font=("Segoe UI", 14, "bold"), bg="white", fg="#1E293B").pack(
                 pady=(20, 4), padx=24, anchor="w")
        tk.Label(win, text="Selecciona el producto para generar su historial completo.",
                 font=("Segoe UI", 9), bg="white", fg="#64748B").pack(
                 padx=24, anchor="w")
        tk.Frame(win, bg="#E2E8F0", height=1).pack(fill="x", padx=24, pady=12)

        # Buscador dentro del diálogo
        tk.Label(win, text="Buscar:", font=("Segoe UI", 9, "bold"),
                 bg="white", fg="#475569").pack(anchor="w", padx=24)

        en_b = tk.Entry(win, font=("Segoe UI", 11), bd=1, relief="solid")
        en_b.pack(fill="x", padx=24, ipady=6, pady=(4, 8))

        lb = tk.Listbox(win, font=("Segoe UI", 10), height=8, bd=1,
                        relief="solid", selectbackground="#EEF2FF",
                        selectforeground="#4361EE", activestyle="none")
        lb.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        prods = Producto.obtener_todos()

        def actualizar_lb(txt=""):
            lb.delete(0, tk.END)
            for p in prods:
                if txt.lower() in p["nombre"].lower():
                    lb.insert(tk.END,
                              f"{p['id_producto']} — {p['nombre']}  (Stock: {p['stock']})")

        actualizar_lb()
        en_b.bind("<KeyRelease>", lambda e: actualizar_lb(en_b.get()))

        def generar():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Selección",
                    "Selecciona un producto.", parent=win)
                return
            linea    = lb.get(sel[0])
            id_p     = int(linea.split(" — ")[0])
            nombre_p = linea.split(" — ")[1].split("  (")[0]
            win.destroy()
            from reportes import generar_kardex
            generar_kardex(id_p, nombre_p)

        tk.Button(win, text="📄  Generar PDF", command=generar,
                  bg="#4361EE", fg="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), cursor="hand2",
                  padx=20, pady=8).pack(fill="x", padx=24, pady=(0, 20))