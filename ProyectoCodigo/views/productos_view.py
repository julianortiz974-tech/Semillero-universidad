import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from PIL import Image, ImageTk
from models.modelos import Producto, Categoria

class VentanaProductos:
    def __init__(self, container):
        self.container = container
        self.bg_color = "#F4F6F9"
        self.primary_color = "#111827" 
        
        for widget in self.container.winfo_children(): 
            widget.destroy()
            
        self.ruta_img = os.path.join(os.getcwd(), "assets", "productos")
        os.makedirs(self.ruta_img, exist_ok=True)

        self._configurar_estilos()
        self._construir_interfaz()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white", rowheight=35, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#E2E8F0", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", "#EFF6FF")], foreground=[("selected", "#111827")])

    def _construir_interfaz(self):
        header = tk.Frame(self.container, bg=self.bg_color)
        header.pack(fill="x", padx=40, pady=(30, 20))
        tk.Label(header, text="Inventario", font=("Segoe UI", 24, "bold"), bg=self.bg_color, fg="#111827").pack(side="left")

        btn_nuevo = tk.Button(header, text="+ Nuevo", command=self.abrir_formulario, bg=self.primary_color, fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8, cursor="hand2")
        btn_nuevo.pack(side="right")

        action_bar = tk.Frame(self.container, bg=self.bg_color)
        action_bar.pack(fill="x", padx=40, pady=(0, 15))

        search_frame = tk.Frame(action_bar, bg="white", bd=1, relief="solid")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 20))
        tk.Label(search_frame, text="🔍", bg="white", fg="gray").pack(side="left", padx=10)
        self.ent_buscar = tk.Entry(search_frame, font=("Segoe UI", 10), bd=0, width=40)
        self.ent_buscar.insert(0, "Buscar por nombre...")
        self.ent_buscar.pack(side="left", fill="x", expand=True, pady=8)
        self.ent_buscar.bind("<FocusIn>", lambda e: self.ent_buscar.delete(0, tk.END) if "Buscar" in self.ent_buscar.get() else None)
        self.ent_buscar.bind("<KeyRelease>", self.buscar_producto)

        tk.Button(action_bar, text="Editar", command=lambda: self.abrir_formulario(editar=True), bg="white", fg="#111827", bd=1, relief="solid", font=("Segoe UI", 10), padx=15).pack(side="right", padx=5)
        tk.Button(action_bar, text="Eliminar", command=self.eliminar_producto, bg="#FEE2E2", fg="#EF4444", bd=0, font=("Segoe UI", 10), padx=15).pack(side="right", padx=5)

        table_frame = tk.Frame(self.container, bg="white", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=40, pady=(0, 30))

        columnas = ("ID", "Producto", "Categoría", "Costo", "Und", "Stock", "Estado")
        self.tabla = ttk.Treeview(table_frame, columns=columnas, show="headings")
        
        anchos = {"ID": 40, "Producto": 250, "Categoría": 150, "Costo": 80, "Und": 50, "Stock": 60, "Estado": 100}
        for col in columnas:
            self.tabla.heading(col, text=col.upper())
            self.tabla.column(col, anchor="center", width=anchos[col])
        
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tabla.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.tabla.tag_configure('critico', background='#FEF2F2', foreground='#991B1B')
        self.tabla.tag_configure('optimo', background='white')

        self.cargar_categorias()
        self.cargar_productos_total()

    def abrir_formulario(self, editar=False):
        if editar and not self.tabla.selection():
            return messagebox.showwarning("Aviso", "Selecciona un producto de la tabla para editar.")

        self.form = tk.Toplevel(self.container)
        self.form.geometry("650x450")
        self.form.title("Nuevo Producto" if not editar else "Editar Producto")
        self.form.config(bg="white")
        self.form.grab_set()
        self.form.resizable(False, False)

        # 1. Traer categorías actualizadas
        from models.modelos import Categoria, Producto
        self.lista_categorias = Categoria.obtener_todas()
        nombres_cat = [c['nombre_categoria'] for c in self.lista_categorias]

        self.img_path_var = tk.StringVar(value="")
        p_id = p_nom = p_desc = p_cost = p_sto = p_min = p_img = ""
        p_und = "Unidad (und)"
        p_cat_nombre = "" # Para preseleccionar si estamos editando
        
        if editar:
            item = self.tabla.selection()[0]
            val = self.tabla.item(item)['values']
            p_id = val[0]
            for p in Producto.obtener_todos():
                if p['id_producto'] == p_id:
                    p_nom = p['nombre']
                    p_desc = p['descripcion']
                    p_cost = p['costo']
                    p_und = p['unidad']
                    p_sto = p['stock']
                    p_min = p['stock_minimo']
                    p_img = p['imagen_path']
                    p_cat_nombre = p['nombre_categoria'] # Asumimos que la consulta trae el nombre
                    self.img_path_var.set(p_img if p_img else "")
                    break

        tk.Label(self.form, text="Nuevo Producto" if not editar else "Editar Producto", font=("Segoe UI", 16, "bold"), bg="white", fg="#111827").place(x=30, y=20)
        tk.Button(self.form, text="✕", command=self.form.destroy, bg="white", bd=0, font=("Arial", 14), cursor="hand2").place(x=600, y=20)

        # --- SECCIÓN IMAGEN ---
        frame_img = tk.Frame(self.form, bg="white", width=180, height=180, highlightbackground="#E2E8F0", highlightthickness=1)
        frame_img.place(x=30, y=80)
        frame_img.pack_propagate(False)

        self.lbl_img = tk.Label(frame_img, bg="#F8FAFC", text="📸\nSin Imagen", font=("Segoe UI", 10), fg="#94A3B8")
        self.lbl_img.pack(fill="both", expand=True)
        tk.Button(self.form, text="Subir Imagen", command=self.cargar_imagen, bg="white", bd=1, relief="solid", font=("Segoe UI", 9)).place(x=70, y=270)

        if p_img and os.path.exists(p_img):
            self.mostrar_preview(p_img)

        # --- SECCIÓN FORMULARIO ---
        frame_form = tk.Frame(self.form, bg="white")
        frame_form.place(x=240, y=80, width=380)

        # Fila 1: Nombre
        tk.Label(frame_form, text="Nombre del Producto *", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        self.en_nom = tk.Entry(frame_form, font=("Segoe UI", 10), bg="#F8FAFC", bd=1, relief="solid", width=42)
        self.en_nom.insert(0, p_nom); self.en_nom.grid(row=1, column=0, columnspan=2, pady=(0, 15), ipady=5)

        # Fila 2: Categoría (Conectada a la BD) y Unidad
        tk.Label(frame_form, text="Categoría *", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=2, column=0, sticky="w", pady=(0, 5))
        tk.Label(frame_form, text="Unidad", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=2, column=1, sticky="w", pady=(0, 5), padx=(10,0))
        
        self.cb_categoria = ttk.Combobox(frame_form, values=nombres_cat, state="readonly", width=18)
        # Si estamos editando y tiene categoría, la ponemos. Si no, ponemos la primera disponible.
        if editar and p_cat_nombre in nombres_cat:
            self.cb_categoria.set(p_cat_nombre)
        elif nombres_cat:
            self.cb_categoria.current(0)
        self.cb_categoria.grid(row=3, column=0, pady=(0, 15), ipady=4)

        self.cb_und = ttk.Combobox(frame_form, values=["Unidad (und)", "Kilogramo (kg)", "Litro (l)", "Caja"], state="readonly", width=18)
        self.cb_und.set(p_und); self.cb_und.grid(row=3, column=1, pady=(0, 15), padx=(10,0), ipady=4)

        # Fila 3: Costo y Stock Mínimo
        tk.Label(frame_form, text="Costo ($)", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=4, column=0, sticky="w", pady=(0, 5))
        tk.Label(frame_form, text="Stock Mínimo", bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").grid(row=4, column=1, sticky="w", pady=(0, 5), padx=(10,0))

        self.en_cost = tk.Entry(frame_form, font=("Segoe UI", 10), bg="#F8FAFC", bd=1, relief="solid", width=20)
        self.en_cost.insert(0, p_cost if p_cost else "0.00"); self.en_cost.grid(row=5, column=0, pady=(0, 15), ipady=5)

        self.en_min = tk.Entry(frame_form, font=("Segoe UI", 10), bg="#F8FAFC", bd=1, relief="solid", width=20)
        self.en_min.insert(0, p_min if str(p_min) else "5"); self.en_min.grid(row=5, column=1, pady=(0, 15), padx=(10,0), ipady=5)

        # Botones de Acción
        frame_btns = tk.Frame(self.form, bg="white")
        frame_btns.place(x=240, y=390, width=380)
        
        tk.Button(frame_btns, text="Cancelar", command=self.form.destroy, bg="white", fg="#475569", bd=0, font=("Segoe UI", 10)).pack(side="right", padx=(10, 0))
        cmd = lambda: self.guardar_producto(editar, p_id)
        tk.Button(frame_btns, text="Guardar Producto", command=cmd, bg=self.primary_color, fg="white", bd=0, font=("Segoe UI", 10, "bold"), padx=15, pady=5).pack(side="right")

    def cargar_categorias(self):
        self.categorias_data = Categoria.obtener_todas()

    def cargar_productos_total(self):
        self.actualizar_tabla(Producto.obtener_todos())

    def actualizar_tabla(self, lista):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        for p in lista:
            stock = int(p['stock'])
            minimo = int(p['stock_minimo'])
            estado = "Crítico" if stock <= minimo else "Óptimo"
            tag = 'critico' if stock <= minimo else 'optimo'

            self.tabla.insert("", "end", values=(
                p['id_producto'], p['nombre'], p['nombre_categoria'], f"${p['costo']}", p['unidad'], stock, estado
            ), tags=(tag,))

    def buscar_producto(self, event):
        t = self.ent_buscar.get().lower()
        if "buscar" in t: return
        # Buscamos solo por nombre ahora
        self.actualizar_tabla([p for p in Producto.obtener_todos() if t in str(p['nombre']).lower()])

    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if ruta:
            nombre_archivo = os.path.basename(ruta)
            
            # 1. Calculamos la ruta base real (subiendo un nivel desde la carpeta views)
            directorio_base = os.path.dirname(os.path.dirname(__file__))
            
            # 2. Definimos la carpeta exacta donde deben ir las fotos de productos
            carpeta_destino = os.path.join(directorio_base, "assets", "productos")
            
            # 3. ¡EL TRUCO MÁGICO! Le decimos a Python que cree la carpeta si no existe
            os.makedirs(carpeta_destino, exist_ok=True)
            
            # 4. Pegamos la imagen en el destino seguro
            destino = os.path.join(carpeta_destino, nombre_archivo)
            shutil.copy(ruta, destino)
            
            # 5. Guardamos la ruta en la variable y actualizamos la vista
            self.img_path_var.set(destino)
            self.mostrar_preview(destino)
            messagebox.showinfo("Éxito", "Imagen cargada correctamente para este producto.")

    def mostrar_preview(self, ruta):
        try:
            img = Image.open(ruta)
            img = img.resize((178, 178))
            self.img_tk = ImageTk.PhotoImage(img)
            self.lbl_img.config(image=self.img_tk, text="")
        except:
            pass

    def guardar_producto(self, editar=False, p_id=None):
        nombre = self.en_nom.get().strip()
        costo = self.en_cost.get().strip()
        minimo = self.en_min.get().strip()
        unidad = self.cb_und.get()
        img_path = self.img_path_var.get()
        
        # --- PROCESAR LA CATEGORÍA (Mapeo Relacional) ---
        nombre_cat_seleccionada = self.cb_categoria.get()
        id_cat_final = None

        for c in self.lista_categorias:
            if c['nombre_categoria'] == nombre_cat_seleccionada:
                id_cat_final = c['id_categoria']
                break

        if not nombre or not id_cat_final:
            return messagebox.showerror("Error", "El nombre y la categoría son campos obligatorios.")

        try:
            costo_float = float(costo)
            minimo_int = int(minimo)
        except ValueError:
            return messagebox.showerror("Error", "Costo y Stock Mínimo deben ser valores numéricos válidos.")

        from models.modelos import Producto
        
        # En la creación inicial, el stock siempre es 0 (se llena luego con un movimiento de Entrada)
        # La descripción la dejamos vacía por ahora ya que la quitamos del form visual para simplificar
        p = Producto(nombre, "", costo_float, unidad, 0, minimo_int, img_path, id_cat_final, p_id)

        exito = p.actualizar() if editar else p.insertar()
        
        if exito:
            self.form.destroy()
            self.cargar_productos_total() # Refresca la tabla
            messagebox.showinfo("Éxito", "Producto guardado correctamente.")
        else:
            messagebox.showerror("Error", "Ocurrió un error al intentar guardar en la base de datos.")
    def eliminar_producto(self):
        # 1. Validar que haya algo seleccionado
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona un producto de la tabla.")
            return

        # 2. Tomar el elemento seleccionado
        item = seleccion[0]
        
        # 3. Extraer ID y Nombre (¡Sintaxis corregida sin el [0] extra!)
        id_p = self.tabla.item(item)['values'][0]
        nombre_p = self.tabla.item(item)['values'][1]

        # 4. Confirmar con el usuario
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar '{nombre_p}'?\nNota: Solo se pueden eliminar productos sin historial de movimientos."):
            from models.modelos import Producto
            
            # 5. Intentar eliminar en la base de datos
            if Producto.eliminar(id_p):
                self.cargar_productos_total() # Refresca la tabla
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            else:
                # Aquí entra la protección de tu Kardex
                messagebox.showerror("Acción Denegada", "No se puede eliminar este producto.\n\nEl sistema lo protege porque ya cuenta con Entradas o Salidas registradas en el historial del Kardex.")