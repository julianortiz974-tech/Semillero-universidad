import tkinter as tk
from tkinter import ttk, messagebox
from models.cliente import Cliente

class VentanaClientes:
    def __init__(self, root, callback_volver):
        self.root = root
        self.callback_volver = callback_volver
        self.id_editando = None # Variable para saber si guardamos o actualizamos

        # Limpiar ventana
        for widget in root.winfo_children(): 
            widget.destroy()
            
        self.root.title("Smart Sales - Gestión de Clientes")
        self.root.geometry("1100x700")
        self.root.configure(bg="#F2E8E4")

        # --- BARRA SUPERIOR GUINDA ---
        top_bar = tk.Frame(root, bg="#712828", height=50)
        top_bar.pack(fill="x")
        
        tk.Button(top_bar, text="⬅", command=self.callback_volver, 
                  bg="#712828", fg="white", relief="flat", 
                  font=("Arial", 18, "bold"), cursor="hand2").pack(side="left", padx=10)
        
        tk.Label(top_bar, text="PANEL DE CLIENTES", font=("Arial", 14, "bold"), 
                 bg="#712828", fg="white").pack(side="left", padx=5)

        # --- CONTENEDOR CENTRAL ---
        main_container = tk.Frame(root, bg="#F2E8E4")
        main_container.pack(padx=30, pady=20, fill="both", expand=True)

        # ==========================================
        # 1. PANEL IZQUIERDO: FORMULARIO
        # ==========================================
        left_panel = tk.Frame(main_container, bg="#F2E8E4", width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="DATOS DEL CLIENTE", font=("Arial", 18, "bold"), 
                 bg="#F2E8E4", fg="#A5525A").pack(anchor="w", pady=(0, 15))

        self.en_nom = self.crear_campo(left_panel, "Nombre Completo *")
        self.en_doc = self.crear_campo(left_panel, "Documento (NIT/CC) *")
        self.en_tel = self.crear_campo(left_panel, "Teléfono")
        self.en_cor = self.crear_campo(left_panel, "Correo Electrónico")
        self.en_dir = self.crear_campo(left_panel, "Dirección")

        # Botones del formulario
        btn_frame = tk.Frame(left_panel, bg="#F2E8E4")
        btn_frame.pack(fill="x", pady=20)
        
        self.btn_guardar = tk.Button(btn_frame, text="GUARDAR", command=self.guardar_cliente, 
                                     bg="#712828", fg="white", font=("Arial", 12, "bold"), cursor="hand2")
        self.btn_guardar.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Button(btn_frame, text="LIMPIAR", command=self.limpiar_form, 
                  bg="#A5525A", fg="white", font=("Arial", 12, "bold"), cursor="hand2").pack(side="right", fill="x", expand=True, padx=(5, 0))

        # ==========================================
        # 2. PANEL DERECHO: BUSCADOR, TABLA Y ESTADÍSTICAS
        # ==========================================
        right_panel = tk.Frame(main_container, bg="#F2E8E4")
        right_panel.pack(side="right", fill="both", expand=True)

        # --- Buscador superior ---
        search_frame = tk.Frame(right_panel, bg="#F2E8E4")
        search_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(search_frame, text="🔍 Buscar:", bg="#F2E8E4", font=("Arial", 12, "bold"), fg="#712828").pack(side="left")
        self.en_buscar = tk.Entry(search_frame, font=("Arial", 12), width=30)
        self.en_buscar.pack(side="left", padx=10)
        self.en_buscar.bind("<KeyRelease>", self.filtrar_tabla) # Busca mientras escribes

        btn_acciones = tk.Frame(search_frame, bg="#F2E8E4")
        btn_acciones.pack(side="right")
        tk.Button(btn_acciones, text="Editar Seleccionado", command=self.cargar_para_edicion, bg="#C48B7A", fg="white", cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_acciones, text="Eliminar", command=self.eliminar_cliente, bg="#712828", fg="white", cursor="hand2").pack(side="left")

        # --- Tabla de Clientes (Treeview) ---
        self.configurar_estilo_tabla()
        columnas = ("ID", "Documento", "Nombre", "Teléfono", "Correo")
        self.tabla = ttk.Treeview(right_panel, columns=columnas, show="headings", height=15)
        
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Documento", text="DOCUMENTO")
        self.tabla.heading("Nombre", text="NOMBRE")
        self.tabla.heading("Teléfono", text="TELÉFONO")
        self.tabla.heading("Correo", text="CORREO")
        
        self.tabla.column("ID", width=30, anchor="center")
        self.tabla.column("Documento", width=100)
        self.tabla.column("Nombre", width=200)
        self.tabla.column("Teléfono", width=100, anchor="center")
        self.tabla.column("Correo", width=150)
        
        self.tabla.pack(fill="both", expand=True)
        self.tabla.bind("<Double-1>", lambda e: self.cargar_para_edicion())

        # --- Sección de Estadísticas (Inspirado en tu Mockup) ---
        stats_frame = tk.Frame(right_panel, bg="white", bd=1, relief="solid")
        stats_frame.pack(fill="x", pady=(15, 0), ipady=10)
        
        tk.Label(stats_frame, text="ESTADÍSTICAS DEL CLIENTE SELECCIONADO", font=("Arial", 10, "bold"), bg="white", fg="#A5525A").pack(anchor="w", padx=10, pady=5)
        
        info_frame = tk.Frame(stats_frame, bg="white")
        info_frame.pack(fill="x", padx=10)
        
        self.lbl_compras = tk.Label(info_frame, text="Total Comprado: $0.00 (Próximamente en Módulo Ventas)", bg="white", font=("Arial", 10))
        self.lbl_compras.pack(side="left")

        # Cargar datos iniciales
        self.cargar_tabla()

    # --- MÉTODOS DE LA CLASE ---

    def crear_campo(self, master, texto):
        tk.Label(master, text=texto, bg="#F2E8E4", fg="#712828", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 2))
        e = tk.Entry(master, font=("Arial", 12), bd=1, relief="solid")
        e.pack(fill="x", pady=2, ipady=3)
        return e

    def configurar_estilo_tabla(self):
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview.Heading", background="#712828", foreground="white", font=("Arial", 10, "bold"))
        estilo.configure("Treeview", background="white", fieldbackground="white", rowheight=25)
        estilo.map("Treeview", background=[("selected", "#C48B7A")])

    def cargar_tabla(self, filtro=""):
        """Carga los datos en la tabla leyendo el diccionario de la BD"""
        # Limpiar tabla primero
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        clientes = Cliente.obtener_todos()
        
        # Validar si no hay clientes aún
        if not clientes: return 

        for c in clientes:
            # Extraemos los datos usando los nombres de las columnas de MySQL
            id_cli = c['id_cliente']
            doc = str(c['documento'])
            nom = str(c['nombre'])
            tel = str(c['telefono']) if c['telefono'] else ""
            cor = str(c['correo']) if c['correo'] else ""
            
            # Filtro simple por nombre o documento
            if filtro.lower() in nom.lower() or filtro.lower() in doc.lower():
                self.tabla.insert("", "end", values=(id_cli, doc, nom, tel, cor))

    def filtrar_tabla(self, event):
        self.cargar_tabla(self.en_buscar.get())

    def limpiar_form(self):
        self.id_editando = None
        self.btn_guardar.config(text="GUARDAR", bg="#712828")
        for en in [self.en_nom, self.en_doc, self.en_tel, self.en_cor, self.en_dir]:
            en.delete(0, tk.END)

    def guardar_cliente(self):
        nom = self.en_nom.get().strip()
        doc = self.en_doc.get().strip()
        tel = self.en_tel.get().strip()
        cor = self.en_cor.get().strip()
        dire = self.en_dir.get().strip()

        if not nom or not doc:
            return messagebox.showwarning("Advertencia", "El Nombre y el Documento son obligatorios.")

        try:
            if self.id_editando:
                Cliente.actualizar(self.id_editando, nom, doc, tel, cor, dire)
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
            else:
                Cliente.agregar(nom, doc, tel, cor, dire)
                messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
            
            self.limpiar_form()
            self.cargar_tabla()
        except Exception as e:
            messagebox.showerror("Error BD", f"Error al guardar: {e}\n(Revise que el documento no esté duplicado)")

    def cargar_para_edicion(self):
        """Pasa los datos de la tabla al formulario para editarlos"""
        seleccion = self.tabla.focus()
        if not seleccion:
            return messagebox.showwarning("Aviso", "Seleccione un cliente de la tabla.")
            
        valores = self.tabla.item(seleccion)['values']
        self.limpiar_form()
        
        # valores[0] es ID, [1] Documento, [2] Nombre, [3] Teléfono, [4] Correo
        self.id_editando = valores[0]
        
        # Llenamos el formulario
        self.en_doc.insert(0, valores[1])
        self.en_nom.insert(0, valores[2])
        self.en_tel.insert(0, valores[3] if valores[3] != "None" else "")
        self.en_cor.insert(0, valores[4] if valores[4] != "None" else "")
        
        # Buscamos la dirección directamente en la BD porque no está en la tabla visual
        cliente_completo = Cliente.buscar_por_documento(valores[1])
        if cliente_completo and cliente_completo['direccion']:
            self.en_dir.insert(0, cliente_completo['direccion'])
        
        self.btn_guardar.config(text="ACTUALIZAR", bg="#C48B7A")

    def eliminar_cliente(self):
        seleccion = self.tabla.focus()
        if not seleccion:
            return messagebox.showwarning("Aviso", "Seleccione un cliente para eliminar.")
            
        id_cli = self.tabla.item(seleccion)['values'][0]
        nombre = self.tabla.item(seleccion)['values'][2]
        
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar (dar de baja) al cliente {nombre}?"):
            try:
                Cliente.eliminar(id_cli)
                self.cargar_tabla()
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")