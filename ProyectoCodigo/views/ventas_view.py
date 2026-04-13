import tkinter as tk
from tkinter import ttk, messagebox
from models.cliente import Cliente
from models.venta import Venta
from models.productos import Producto 

class VentanaVentas:
    def __init__(self, root, callback_volver):
        self.root = root
        self.callback_volver = callback_volver
        
        # Variables de la venta actual
        self.cliente_actual = None
        self.producto_actual = None
        self.carrito = [] # Lista para guardar los productos añadidos
        self.total_venta = 0.0

        # Limpiar ventana
        for widget in root.winfo_children(): 
            widget.destroy()
            
        self.root.title("Smart Sales - Punto de Venta")
        self.root.geometry("1100x700")
        self.root.configure(bg="#F2E8E4")

        # --- BARRA SUPERIOR ---
        top_bar = tk.Frame(root, bg="#712828", height=50)
        top_bar.pack(fill="x")
        
        tk.Button(top_bar, text="⬅", command=self.callback_volver, 
                  bg="#712828", fg="white", relief="flat", 
                  font=("Arial", 18, "bold"), cursor="hand2").pack(side="left", padx=10)
        
        tk.Label(top_bar, text="NUEVA VENTA", font=("Arial", 14, "bold"), 
                 bg="#712828", fg="white").pack(side="left", padx=5)

        # --- CONTENEDOR PRINCIPAL ---
        main_container = tk.Frame(root, bg="#F2E8E4")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # ==========================================
        # PANEL IZQUIERDO: BÚSQUEDA (Cliente y Producto)
        # ==========================================
        left_panel = tk.Frame(main_container, bg="#F2E8E4", width=400)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)

        # --- SECCIÓN 1: DATOS DEL CLIENTE ---
        frame_cliente = tk.LabelFrame(left_panel, text=" 1. Buscar Cliente ", bg="#F2E8E4", fg="#712828", font=("Arial", 12, "bold"))
        frame_cliente.pack(fill="x", pady=(0, 15), ipady=10)

        tk.Label(frame_cliente, text="Documento (NIT/CC):", bg="#F2E8E4", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        
        search_cli_frame = tk.Frame(frame_cliente, bg="#F2E8E4")
        search_cli_frame.pack(fill="x", padx=10)
        
        self.en_doc_cliente = tk.Entry(search_cli_frame, font=("Arial", 12), width=20)
        self.en_doc_cliente.pack(side="left", padx=(0, 10))
        self.en_doc_cliente.bind("<Return>", lambda e: self.buscar_cliente()) # Buscar al presionar Enter
        
        tk.Button(search_cli_frame, text="Buscar", command=self.buscar_cliente, bg="#A5525A", fg="white", cursor="hand2").pack(side="left")

        self.lbl_nombre_cliente = tk.Label(frame_cliente, text="Cliente: (Ninguno seleccionado)", bg="#F2E8E4", fg="black", font=("Arial", 11, "bold"))
        self.lbl_nombre_cliente.pack(anchor="w", padx=10, pady=10)

        # --- SECCIÓN 2: DATOS DEL PRODUCTO ---
        frame_prod = tk.LabelFrame(left_panel, text=" 2. Buscar Producto ", bg="#F2E8E4", fg="#712828", font=("Arial", 12, "bold"))
        frame_prod.pack(fill="x", pady=10, ipady=10)

        tk.Label(frame_prod, text="Código del Producto:", bg="#F2E8E4", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
        
        search_prod_frame = tk.Frame(frame_prod, bg="#F2E8E4")
        search_prod_frame.pack(fill="x", padx=10)
        
        self.en_cod_producto = tk.Entry(search_prod_frame, font=("Arial", 12), width=20)
        self.en_cod_producto.pack(side="left", padx=(0, 10))
        self.en_cod_producto.bind("<Return>", lambda e: self.buscar_producto())
        
        tk.Button(search_prod_frame, text="Buscar", command=self.buscar_producto, bg="#A5525A", fg="white", cursor="hand2").pack(side="left")

        self.lbl_info_prod = tk.Label(frame_prod, text="Producto: -\nStock: -\nPrecio: $0.00", bg="#F2E8E4", fg="blue", font=("Arial", 11), justify="left")
        self.lbl_info_prod.pack(anchor="w", padx=10, pady=10)

        # --- SECCIÓN 3: CANTIDAD Y AGREGAR ---
        frame_add = tk.Frame(frame_prod, bg="#F2E8E4")
        frame_add.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_add, text="Cantidad:", bg="#F2E8E4", font=("Arial", 12, "bold")).pack(side="left")
        self.en_cantidad = tk.Entry(frame_add, font=("Arial", 12), width=8, justify="center")
        self.en_cantidad.insert(0, "1")
        self.en_cantidad.pack(side="left", padx=10)
        self.en_cantidad.bind("<Return>", lambda e: self.agregar_al_carrito())

        tk.Button(frame_prod, text="➕ AGREGAR AL CARRITO", command=self.agregar_al_carrito, 
                  bg="#712828", fg="white", font=("Arial", 12, "bold"), pady=5, cursor="hand2").pack(fill="x", padx=10, pady=15)


        # ==========================================
        # PANEL DERECHO: CARRITO Y TOTALES
        # ==========================================
        right_panel = tk.Frame(main_container, bg="white", bd=1, relief="solid")
        right_panel.pack(side="right", fill="both", expand=True)

        tk.Label(right_panel, text="🛒 DETALLE DE LA VENTA", font=("Arial", 14, "bold"), bg="white", fg="#712828").pack(pady=10)

        # Tabla del Carrito
        self.configurar_estilo_tabla()
        columnas = ("ID", "Producto", "Cantidad", "P. Unitario", "Subtotal")
        self.tabla = ttk.Treeview(right_panel, columns=columnas, show="headings", height=12)
        
        for col in columnas:
            self.tabla.heading(col, text=col.upper())
            
        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Producto", width=250)
        self.tabla.column("Cantidad", width=80, anchor="center")
        self.tabla.column("P. Unitario", width=100, anchor="e")
        self.tabla.column("Subtotal", width=100, anchor="e")
        
        self.tabla.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Button(right_panel, text="❌ Quitar Seleccionado", command=self.quitar_del_carrito, bg="#C48B7A", fg="white", cursor="hand2").pack(anchor="e", padx=10)

        # --- SECCIÓN DE COBRO ---
        cobro_frame = tk.Frame(right_panel, bg="#F2E8E4", bd=1, relief="solid")
        cobro_frame.pack(fill="x", side="bottom")

        # Checkbox para el correo (Preparando el terreno para el envío)
        self.enviar_correo_var = tk.BooleanVar(value=True)
        tk.Checkbutton(cobro_frame, text="📧 Enviar factura al correo del cliente", variable=self.enviar_correo_var, 
                       bg="#F2E8E4", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(15, 0))

        total_frame = tk.Frame(cobro_frame, bg="#F2E8E4")
        total_frame.pack(fill="x", padx=20, pady=15)

        self.lbl_total = tk.Label(total_frame, text="TOTAL: $0.00", font=("Arial", 28, "bold"), bg="#F2E8E4", fg="#712828")
        self.lbl_total.pack(side="left")

        tk.Button(total_frame, text="💰 FACTURAR Y GUARDAR", command=self.procesar_venta, 
                  bg="#712828", fg="white", font=("Arial", 16, "bold"), padx=20, cursor="hand2").pack(side="right")


    # --- MÉTODOS DE LÓGICA (CONECTADOS A LA BD) ---

    def configurar_estilo_tabla(self):
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview.Heading", background="#712828", foreground="white", font=("Arial", 10, "bold"))
        estilo.configure("Treeview", background="white", rowheight=25)

    def buscar_cliente(self):
        doc = self.en_doc_cliente.get().strip()
        if not doc: return
        
        try:
            # Usamos la función que creamos en el módulo de clientes
            cliente = Cliente.buscar_por_documento(doc)
            if cliente:
                self.cliente_actual = cliente
                self.lbl_nombre_cliente.config(text=f"Cliente: {cliente['nombre']}", fg="green")
            else:
                self.cliente_actual = None
                self.lbl_nombre_cliente.config(text="Cliente: No encontrado", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar cliente: {e}")

    def buscar_producto(self):
        """Busca el producto por ID y muestra su info en pantalla"""
        cod = self.en_cod_producto.get().strip()
        if not cod: return
        
        try:
            producto = Producto.obtener_por_id(cod)
            if producto:
                self.producto_actual = producto
                # Actualizamos la etiqueta azul con los datos reales
                self.lbl_info_prod.config(
                    text=f"Producto: {producto['nombre']}\nStock: {producto['stock']} unidades\nPrecio: ${float(producto['precio']):,.2f}", 
                    fg="blue"
                )
                self.en_cantidad.focus() # Pasa el cursor a "Cantidad" automáticamente
            else:
                self.producto_actual = None
                self.lbl_info_prod.config(text="Producto: No encontrado\nStock: -\nPrecio: $0.00", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar producto: {e}")

    def agregar_al_carrito(self):
        """Valida stock, calcula subtotales y añade a la tabla visual"""
        if not self.producto_actual:
            return messagebox.showwarning("Aviso", "Primero busque y seleccione un producto.")

        try:
            cantidad = int(self.en_cantidad.get().strip())
            if cantidad <= 0: raise ValueError
        except ValueError:
            return messagebox.showwarning("Aviso", "Ingrese una cantidad válida mayor a 0.")

        # Validar si hay stock suficiente
        stock_disponible = int(self.producto_actual['stock'])
        
        # Revisar si ya agregamos de este mismo producto al carrito antes para no pasarnos del stock
        cantidad_en_carrito = sum(item['cantidad'] for item in self.carrito if item['id_producto'] == self.producto_actual['id_producto'])

        if (cantidad + cantidad_en_carrito) > stock_disponible:
            return messagebox.showwarning("Stock Insuficiente", 
                                          f"Solo hay {stock_disponible} unidades disponibles.\nYa tienes {cantidad_en_carrito} en el carrito.")

        # Cálculos matemáticos
        precio = float(self.producto_actual['precio'])
        subtotal = cantidad * precio

        # 1. Guardar en nuestra lista interna (Backend)
        item_carrito = {
            'id_producto': self.producto_actual['id_producto'],
            'nombre': self.producto_actual['nombre'],
            'cantidad': cantidad,
            'precio_unitario': precio,
            'subtotal': subtotal
        }
        self.carrito.append(item_carrito)

        # 2. Mostrar en la tabla (Frontend)
        self.tabla.insert("", "end", values=(
            item_carrito['id_producto'],
            item_carrito['nombre'],
            item_carrito['cantidad'],
            f"${precio:,.2f}",
            f"${subtotal:,.2f}"
        ))

        # 3. Limpiar los campos para escanear el siguiente producto
        self.actualizar_total()
        self.en_cod_producto.delete(0, tk.END)
        self.en_cantidad.delete(0, tk.END)
        self.en_cantidad.insert(0, "1")
        self.producto_actual = None
        self.lbl_info_prod.config(text="Producto: -\nStock: -\nPrecio: $0.00", fg="blue")
        self.en_cod_producto.focus()

    def quitar_del_carrito(self):
        """Elimina un producto seleccionado de la tabla y resta del total"""
        seleccion = self.tabla.focus()
        if not seleccion:
            return messagebox.showwarning("Aviso", "Seleccione un producto del carrito para quitar.")

        valores = self.tabla.item(seleccion)['values']
        id_prod = int(valores[0])

        # Quitar de la tabla visual
        self.tabla.delete(seleccion)

        # Buscar en la lista interna y eliminarlo
        for i, item in enumerate(self.carrito):
            if item['id_producto'] == id_prod:
                self.carrito.pop(i)
                break

        self.actualizar_total()

    def actualizar_total(self):
        """Suma todos los subtotales del carrito y actualiza el letrero grande"""
        self.total_venta = sum(item['subtotal'] for item in self.carrito)
        self.lbl_total.config(text=f"TOTAL: ${self.total_venta:,.2f}")
    def procesar_venta(self):
        """Guarda la venta en la BD, descuenta stock y prepara la pantalla para otra venta"""
        if not self.cliente_actual:
            return messagebox.showwarning("Aviso", "Debe buscar y seleccionar un cliente primero.")
        
        if not self.carrito:
            return messagebox.showwarning("Aviso", "El carrito está vacío. Agregue productos.")
            
        if messagebox.askyesno("Confirmar Venta", f"¿Desea registrar esta venta por un total de ${self.total_venta:,.2f}?"):
            try:
                # 1. Llamamos a nuestro Modelo para hacer la magia en MySQL
                id_venta = Venta.registrar_venta(self.cliente_actual['id_cliente'], self.total_venta, self.carrito)
                
                # 2. Mensaje de éxito
                messagebox.showinfo("Éxito", f"¡Venta #{id_venta} registrada correctamente!\nEl inventario ha sido descontado.")
                
                # 3. Aquí iría la lógica del PDF y el Correo (¡Nuestro próximo paso!)
                if self.enviar_correo_var.get():
                    messagebox.showinfo("Facturación", f"Preparando factura en PDF para enviar a: {self.cliente_actual['correo']}")
                
                # 4. Limpiamos toda la pantalla para atender al siguiente cliente
                self.limpiar_pantalla_venta()
                
            except Exception as e:
                messagebox.showerror("Error en BD", f"Ocurrió un error al guardar la venta:\n{e}")

    def limpiar_pantalla_venta(self):
        """Restaura todos los campos a su estado inicial"""
        # Limpiar Cliente
        self.cliente_actual = None
        self.en_doc_cliente.delete(0, tk.END)
        self.lbl_nombre_cliente.config(text="Cliente: (Ninguno seleccionado)", fg="black")
        
        # Limpiar Producto
        self.producto_actual = None
        self.en_cod_producto.delete(0, tk.END)
        self.en_cantidad.delete(0, tk.END)
        self.en_cantidad.insert(0, "1")
        self.lbl_info_prod.config(text="Producto: -\nStock: -\nPrecio: $0.00", fg="blue")
        
        # Limpiar Carrito
        self.carrito.clear()
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.actualizar_total()