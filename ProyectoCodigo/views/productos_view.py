import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog # <-- Añadimos filedialog aquí
from models.productos import Producto
from models.categoria import Categoria

# --- NUEVOS IMPORTS PARA EL PDF ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os

class VentanaProductos:
    def __init__(self, root, callback_volver):
        self.root = root
        self.callback_volver = callback_volver
        
        # --- 1. BLOQUEO DE VENTANA (Fijo) ---
        # Impide que el usuario estire la ventana principal
        self.root.resizable(True, True) 
        
        # Limpiar la ventana
        for widget in root.winfo_children(): 
            widget.destroy()
        
        self.root.title("Smart Sales - Panel de Inventario")
        self.root.geometry("1100x700")
        self.root.configure(bg="#F2E8E4") # Color crema

        # --- BARRA SUPERIOR ---
        top_bar = tk.Frame(root, bg="#712828", height=50)
        top_bar.pack(fill="x")
        
        tk.Button(top_bar, text="⬅", command=self.callback_volver, 
                  bg="#712828", fg="white", relief="flat", font=("Arial", 18, "bold"), cursor="hand2").pack(side="left", padx=10)
        
        tk.Label(top_bar, text="PANEL DE INVENTARIO", font=("Arial", 14, "bold"), 
                 bg="#712828", fg="white").pack(side="left", padx=5)

        # --- CUERPO PRINCIPAL ---
        main_body = tk.Frame(root, bg="#F2E8E4")
        main_body.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. SECCIÓN IZQUIERDA
        left_panel = tk.Frame(main_body, bg="#F2E8E4", width=220)
        left_panel.pack(side="left", fill="y", padx=(0, 20))

        search_frame = tk.Frame(left_panel, bg="white", bd=1, relief="solid")
        search_frame.pack(fill="x", pady=(0, 15))
        tk.Label(search_frame, text="🔍", bg="white").pack(side="left", padx=5)
        self.ent_buscar = tk.Entry(search_frame, font=("Arial", 10), bd=0)
        self.ent_buscar.insert(0, "Buscar...")
        self.ent_buscar.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        self.ent_buscar.bind("<FocusIn>", lambda e: self.ent_buscar.delete(0, tk.END) if self.ent_buscar.get() == "Buscar..." else None)
        self.ent_buscar.bind("<KeyRelease>", self.buscar_producto)

        cat_box = tk.LabelFrame(left_panel, text="CATEGORIAS", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        cat_box.pack(fill="both", expand=True)
        
        # DEFINIMOS LISTA_CAT ANTES DE CARGARLA
        self.lista_cat = tk.Listbox(cat_box, font=("Arial", 10), bd=0, highlightthickness=0, selectbackground="#A5525A")
        self.lista_cat.pack(fill="both", expand=True)
        self.lista_cat.bind("<<ListboxSelect>>", self.filtrar_por_categoria)

        cat_btns = tk.Frame(cat_box, bg="white")
        cat_btns.pack(fill="x", pady=(10, 0))
        tk.Button(cat_btns, text="NUEVA", command=self.añadir_categoria, bg="#A5525A", fg="white", font=("Arial", 8, "bold")).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(cat_btns, text="BORRAR", command=self.eliminar_categoria, bg="#A5525A", fg="white", font=("Arial", 8, "bold")).pack(side="left", expand=True, fill="x", padx=2)

        # 2. SECCIÓN DERECHA
        right_panel = tk.Frame(main_body, bg="#F2E8E4")
        right_panel.pack(side="right", fill="both", expand=True)

        action_bar = tk.Frame(right_panel, bg="#F2E8E4")
        action_bar.pack(fill="x", pady=(0, 15))
        
        tk.Button(action_bar, text="AÑADIR PRODUCTO", command=self.abrir_formulario_producto, 
                  bg="#A5525A", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5).pack(side="left")
        
        tk.Button(action_bar, text="EDITAR", command=self.abrir_formulario_editar, 
                  bg="#A5525A", fg="white", font=("Arial", 10, "bold"), padx=25, pady=5).pack(side="left", padx=15)
        
        tk.Button(action_bar, text="ELIMINAR SELECCIONADO", command=self.eliminar_producto, 
                  bg="#A5525A", fg="white", font=("Arial", 10, "bold"), padx=15, pady=5).pack(side="left")

        # --- TABLA CON COLUMNAS FIJAS ---
        # Definimos self.tabla antes de cargar productos
        self.tabla = ttk.Treeview(right_panel, columns=("ID", "Producto", "Precio", "Stock", "Categoria", "Desc"), show="headings")
        for col in ["ID", "Producto", "Precio", "Stock", "Categoria"]:
            self.tabla.heading(col, text=col.upper())
            # FIX: Quitamos resizable=False porque no es una opción válida para .column() en tk estándar
            self.tabla.column(col, anchor="center", width=120, stretch=tk.NO)
        
        self.tabla.column("Desc", width=0, stretch=tk.NO)
        self.tabla.pack(fill="both", expand=True)

        # --- VÍNCULO PARA DOBLE CLIC ---
        self.tabla.bind("<Double-1>", self.ver_detalles_producto)

        tk.Button(right_panel, text="REPORTE", command=self.generar_reporte, 
                  bg="#A5525A", fg="white", font=("Arial", 10, "bold"), padx=20).pack(side="right", pady=10)

        # AL FINAL CARGAMOS LOS DATOS (Ahora que ya existen los widgets tabla y lista_cat)
        self.cargar_categorias()
        self.cargar_productos_total()

    # ==========================================
    # --- MÉTODOS DE APOYO ---
    # ==========================================

    def crear_input(self, ventana, texto):
        tk.Label(ventana, text=texto, bg="white", font=("Arial", 10)).pack(pady=(10,0))
        e = tk.Entry(ventana, font=("Arial", 11), bd=1, relief="solid")
        e.pack(pady=5, padx=30, fill="x")
        return e

    def ver_detalles_producto(self, event):
        item = self.tabla.selection()
        if not item: return
        valores = self.tabla.item(item)['values']
        nombre = valores[1]
        descripcion = valores[5] if valores[5] else "Sin descripción."
        messagebox.showinfo(f"Detalles de {nombre}", f"DESCRIPCIÓN:\n\n{descripcion}")

    def actualizar_tabla(self, lista):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        for p in lista:
            self.tabla.insert("", "end", values=(
                p['id_producto'], p['nombre'], f"${p['precio']}", p['stock'], 
                p['nombre_categoria'] if p['nombre_categoria'] else "None", p.get('descripcion', "")))

    def cargar_categorias(self):
        self.lista_cat.delete(0, tk.END)
        self.lista_cat.insert(tk.END, "*VER TODO")
        self.categorias_data = Categoria.obtener_todas()
        for c in self.categorias_data: self.lista_cat.insert(tk.END, f"-{c['nombre_categoria'].upper()}")

    def cargar_productos_total(self):
        self.actualizar_tabla(Producto.obtener_todos())

    def buscar_producto(self, event):
        t = self.ent_buscar.get().lower()
        if t == "buscar...": return
        self.actualizar_tabla([p for p in Producto.obtener_todos() if t in str(p['nombre']).lower()])

    def filtrar_por_categoria(self, event):
        idx = self.lista_cat.curselection()
        if not idx or idx[0] == 0: self.cargar_productos_total()
        else:
            cat_id = self.categorias_data[idx[0]-1]['id_categoria']
            self.actualizar_tabla(Producto.obtener_por_categoria(cat_id))

    # ==========================================
    # --- CRUD CATEGORÍAS ---
    # ==========================================

    def añadir_categoria(self):
        nom = simpledialog.askstring("Categoría", "Nombre:")
        if nom:
            exito, msg = Categoria.insertar(nom.strip())
            if exito: self.cargar_categorias()

    def eliminar_categoria(self):
        idx = self.lista_cat.curselection()
        if not idx or idx[0] == 0: return
        cat = self.categorias_data[idx[0]-1]
        # VALIDACIÓN: Tiene datos adentro?
        if Categoria.contar_productos(cat['id_categoria']) > 0:
            return messagebox.showerror("Error", "Esta categoría tiene productos. No se puede borrar.")
        if messagebox.askyesno("Confirmar", f"¿Borrar '{cat['nombre_categoria']}'?"):
            Categoria.eliminar(cat['id_categoria'])
            self.cargar_categorias()

    # ==========================================
    # --- CRUD PRODUCTOS ---
    # ==========================================

    def abrir_formulario_producto(self):
        self.form = tk.Toplevel(self.root)
        self.form.geometry("400x550")
        self.form.grab_set()
        self.nom_val = self.crear_input(self.form, "Nombre:")
        tk.Label(self.form, text="Descripción:").pack()
        self.des_val = tk.Text(self.form, height=4); self.des_val.pack(padx=30, fill="x")
        self.pre_val = self.crear_input(self.form, "Precio:")
        self.sto_val = self.crear_input(self.form, "Stock:")
        self.cb_cat = ttk.Combobox(self.form, state="readonly")
        self.cb_cat['values'] = [f"{c['id_categoria']} - {c['nombre_categoria']}" for c in self.categorias_data]
        self.cb_cat.pack(pady=10)
        tk.Button(self.form, text="GUARDAR", command=self.guardar_nuevo, bg="#A5525A", fg="white").pack()

    def guardar_nuevo(self):
        try:
            p = Producto(self.nom_val.get(), self.des_val.get("1.0", "end-1c"), float(self.pre_val.get()), int(self.sto_val.get()), int(self.cb_cat.get().split(" - ")[0]))
            p.insertar(); self.form.destroy(); self.cargar_productos_total()
        except: messagebox.showerror("Error", "Datos inválidos")

    def abrir_formulario_editar(self):
        item = self.tabla.selection()
        if not item: return
        val = self.tabla.item(item)['values']
        self.form_edit = tk.Toplevel(self.root)
        self.form_edit.grab_set()
        self.en_nom = self.crear_input(self.form_edit, "Nombre:"); self.en_nom.insert(0, val[1])
        tk.Label(self.form_edit, text="Descripción:").pack()
        self.en_des = tk.Text(self.form_edit, height=4); self.en_des.insert("1.0", val[5]); self.en_des.pack(padx=30, fill="x")
        self.en_pre = self.crear_input(self.form_edit, "Precio:"); self.en_pre.insert(0, str(val[2]).replace('$', ''))
        self.en_sto = self.crear_input(self.form_edit, "Stock:"); self.en_sto.insert(0, val[3])
        self.cb_cat_edit = ttk.Combobox(self.form_edit, state="readonly")
        self.cb_cat_edit['values'] = [f"{c['id_categoria']} - {c['nombre_categoria']}" for c in self.categorias_data]
        self.cb_cat_edit.pack(pady=10)
        tk.Button(self.form_edit, text="ACTUALIZAR", command=lambda: self.guardar_edicion(val[0]), bg="#A5525A", fg="white").pack()

    def guardar_edicion(self, id_p):
        try:
            p = Producto(self.en_nom.get(), self.en_des.get("1.0", "end-1c"), float(self.en_pre.get()), int(self.en_sto.get()), int(self.cb_cat_edit.get().split(" - ")[0]), id_p)
            p.actualizar(); self.form_edit.destroy(); self.cargar_productos_total()
        except: messagebox.showerror("Error", "Revisa los campos")

    def eliminar_producto(self):
        item = self.tabla.selection()
        if item:
            id_p = self.tabla.item(item)['values'][0]
            if messagebox.askyesno("Borrar", "¿Eliminar físicamente de la BD?"):
                Producto.eliminar(id_p); self.cargar_productos_total()
    
    def generar_reporte(self):
        """Genera un reporte PDF profesional con logo, datos de empresa y productos"""
        from models.empresa import Empresa
        from reportlab.platypus import Image, SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        import os

        # 1. OBTENER DATOS (Empresa y Productos)
        datos_e = Empresa.obtener_datos()
        
        idx = self.lista_cat.curselection()
        if not idx or idx[0] == 0:
            cat_nombre = "Todos los Productos"
            productos = Producto.obtener_todos()
        else:
            cat = self.categorias_data[idx[0]-1]
            cat_nombre = cat['nombre_categoria']
            productos = Producto.obtener_por_categoria(cat['id_categoria'])

        if not productos:
            return messagebox.showwarning("Aviso", f"No hay productos en '{cat_nombre}'.")

        # 2. SELECCIONAR RUTA DE GUARDADO
        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            title="Guardar Reporte de Inventario",
            initialfile=f"Reporte_{cat_nombre.replace(' ', '_')}.pdf"
        )
        if not ruta_guardado: return

        # 3. CONSTRUCCIÓN DEL DOCUMENTO
        try:
            doc = SimpleDocTemplate(ruta_guardado, pagesize=letter)
            elementos = []
            estilos = getSampleStyleSheet()

            # --- ENCABEZADO: LOGO + INFO EMPRESA ---
            if datos_e:
                # Intentamos cargar el logo si existe
                if datos_e['ruta_logo'] and os.path.exists(datos_e['ruta_logo']):
                    img_logo = Image(datos_e['ruta_logo'], width=70, height=70)
                    # Tabla para alinear Logo (Izquierda) e Info (Derecha)
                    data_header = [[
                        img_logo, 
                        Paragraph(f"<font size=14><b>{datos_e['nombre']}</b></font><br/>"
                                  f"NIT: {datos_e['nit']}<br/>"
                                  f"Dirección: {datos_e['direccion']}<br/>"
                                  f"Tel: {datos_e['telefono']} | {datos_e['correo']}", estilos['Normal'])
                    ]]
                    header_tab = Table(data_header, colWidths=[100, 350])
                else:
                    # Si no hay logo, solo mostramos el texto
                    data_header = [[Paragraph(f"<font size=16><b>{datos_e['nombre']}</b></font><br/>"
                                              f"NIT: {datos_e['nit']} | Tel: {datos_e['telefono']}", estilos['Normal'])]]
                    header_tab = Table(data_header, colWidths=[450])
                
                header_tab.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
                elementos.append(header_tab)
                elementos.append(Spacer(1, 20))

            # TÍTULO DEL REPORTE
            elementos.append(Paragraph(f"<u>INVENTARIO DETALLADO: {cat_nombre.upper()}</u>", estilos['Heading2']))
            elementos.append(Spacer(1, 15))

            # --- TABLA DE DATOS ---
            data_body = [["ID", "PRODUCTO", "PRECIO", "STOCK", "CATEGORÍA"]]
            for p in productos:
                data_body.append([
                    str(p['id_producto']),
                    p['nombre'],
                    f"${p['precio']}",
                    str(p['stock']),
                    p['nombre_categoria'] if p['nombre_categoria'] else "N/A"
                ])

            # Estilo de la tabla (Colores Smart Sales)
            tabla_prod = Table(data_body, colWidths=[40, 180, 80, 60, 110])
            tabla_prod.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#712828")), # Guinda
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F2E8E4")), # Crema
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elementos.append(tabla_prod)

            # 4. GENERAR ARCHIVO
            doc.build(elementos)
            
            if messagebox.askyesno("Éxito", "PDF generado. ¿Deseas abrirlo?"):
                os.startfile(ruta_guardado)

        except Exception as e:
            messagebox.showerror("Error", f"Fallo al crear PDF: {e}")