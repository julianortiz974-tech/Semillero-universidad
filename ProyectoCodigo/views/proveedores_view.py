import tkinter as tk
from tkinter import ttk, messagebox
from models.modelos import Proveedor

class VentanaProveedores:
    def __init__(self, container):
        self.container = container
        self.bg_color = "#F4F6F9"
        self.primary_color = "#111827"
        
        for widget in self.container.winfo_children(): 
            widget.destroy()

        self._configurar_estilos()
        self._construir_interfaz()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white", rowheight=35, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#E2E8F0", font=("Segoe UI", 10, "bold"), borderwidth=0)

    def _construir_interfaz(self):
        # --- HEADER ---
        header = tk.Frame(self.container, bg=self.bg_color)
        header.pack(fill="x", padx=40, pady=(30, 20))
        tk.Label(header, text="Directorio de Proveedores", font=("Segoe UI", 24, "bold"), bg=self.bg_color, fg="#111827").pack(side="left")

        btn_nuevo = tk.Button(header, text="+ Nuevo Proveedor", command=self.abrir_formulario, bg=self.primary_color, fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8, cursor="hand2")
        btn_nuevo.pack(side="right")

        # --- BARRA DE ACCIONES ---
        action_bar = tk.Frame(self.container, bg=self.bg_color)
        action_bar.pack(fill="x", padx=40, pady=(0, 15))

        search_frame = tk.Frame(action_bar, bg="white", bd=1, relief="solid")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 20))
        tk.Label(search_frame, text="🔍", bg="white", fg="gray").pack(side="left", padx=10)
        self.ent_buscar = tk.Entry(search_frame, font=("Segoe UI", 10), bd=0, width=40)
        self.ent_buscar.insert(0, "Buscar por empresa o contacto...")
        self.ent_buscar.pack(side="left", fill="x", expand=True, pady=8)
        self.ent_buscar.bind("<FocusIn>", lambda e: self.ent_buscar.delete(0, tk.END) if "Buscar" in self.ent_buscar.get() else None)
        self.ent_buscar.bind("<KeyRelease>", self.buscar_proveedor)

        tk.Button(action_bar, text="Editar", command=lambda: self.abrir_formulario(editar=True), bg="white", fg="#111827", bd=1, relief="solid", font=("Segoe UI", 10), padx=15).pack(side="right", padx=5)
        tk.Button(action_bar, text="Eliminar", command=self.eliminar_proveedor, bg="#FEE2E2", fg="#EF4444", bd=0, font=("Segoe UI", 10), padx=15).pack(side="right", padx=5)

        # --- TABLA ---
        table_frame = tk.Frame(self.container, bg="white", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=40, pady=(0, 30))

        # Columnas actualizadas a tu BD
        columnas = ("ID", "Empresa", "Contacto", "Teléfono", "Correo")
        self.tabla = ttk.Treeview(table_frame, columns=columnas, show="headings")
        
        anchos = {"ID": 40, "Empresa": 250, "Contacto": 200, "Teléfono": 120, "Correo": 200}
        for col in columnas:
            self.tabla.heading(col, text=col.upper())
            self.tabla.column(col, anchor="center", width=anchos[col])
        
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tabla.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.cargar_datos()

    def cargar_datos(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        for p in Proveedor.obtener_todos():
            # Desempaquetamos usando las llaves correctas de la tabla
            self.tabla.insert("", "end", values=(
                p['id_proveedor'], p['nombre_empresa'], p['nombre_contacto'], p['telefono'], p['correo']
            ))

    def buscar_proveedor(self, event):
        t = self.ent_buscar.get().lower()
        if "buscar" in t: return
        self.cargar_datos()
        items = self.tabla.get_children()
        for item in items:
            val = self.tabla.item(item)['values']
            # Filtramos por Empresa o Contacto
            if t not in str(val[1]).lower() and t not in str(val[2]).lower():
                self.tabla.delete(item)

    def abrir_formulario(self, editar=False):
        if editar and not self.tabla.selection():
            return messagebox.showwarning("Aviso", "Selecciona un proveedor para editar.")

        self.form = tk.Toplevel(self.container)
        self.form.geometry("500x500")
        self.form.title("Gestión de Proveedor")
        self.form.config(bg="white")
        self.form.grab_set()

        p_id = p_empresa = p_contacto = p_tel = p_correo = ""
        if editar:
            item = self.tabla.selection()[0]
            val = self.tabla.item(item)['values']
            p_id, p_empresa, p_contacto, p_tel, p_correo = val

        tk.Label(self.form, text="Datos del Proveedor", font=("Segoe UI", 16, "bold"), bg="white", fg=self.primary_color).pack(pady=20)
        
        # Campos de texto ajustados a tu diseño
        campos = [
            ("Nombre de la Empresa *", p_empresa), 
            ("Nombre del Contacto", p_contacto), 
            ("Teléfono", p_tel), 
            ("Correo Electrónico", p_correo)
        ]
        self.entries = {}

        for label, value in campos:
            f = tk.Frame(self.form, bg="white")
            f.pack(fill="x", padx=40, pady=5)
            tk.Label(f, text=label, bg="white", font=("Segoe UI", 9, "bold"), fg="#475569").pack(anchor="w")
            en = tk.Entry(f, font=("Segoe UI", 11), bg="#F8FAFC", bd=1, relief="solid")
            en.insert(0, value if value != 'None' else "")
            en.pack(fill="x", pady=2, ipady=5)
            self.entries[label] = en

        btn_f = tk.Frame(self.form, bg="white")
        btn_f.pack(pady=30)
        tk.Button(btn_f, text="Guardar Cambios", bg=self.primary_color, fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=25, pady=10, command=lambda: self.guardar(editar, p_id)).pack()

    def guardar(self, editar, p_id):
        empresa = self.entries["Nombre de la Empresa *"].get()
        contacto = self.entries["Nombre del Contacto"].get()
        tel = self.entries["Teléfono"].get()
        correo = self.entries["Correo Electrónico"].get()

        if not empresa: 
            return messagebox.showerror("Error", "El nombre de la empresa es obligatorio")

        p = Proveedor(empresa, contacto, tel, correo)
        
        exito = p.actualizar(p_id) if editar else p.insertar()
        if exito:
            self.form.destroy()
            self.cargar_datos()
        else:
            messagebox.showerror("Error", "No se pudo procesar la solicitud.")

    def eliminar_proveedor(self):
        item = self.tabla.selection()
        if item:
            id_p = self.tabla.item(item)['values'][0]
            if messagebox.askyesno("Confirmar", "¿Eliminar este proveedor permanentemente?"):
                Proveedor.eliminar(id_p)
                self.cargar_datos()