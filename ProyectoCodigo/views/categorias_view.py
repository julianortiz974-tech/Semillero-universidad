import tkinter as tk
from tkinter import ttk, messagebox
from models.modelos import Categoria

class VentanaCategorias:
    def __init__(self, container):
        self.container = container
        self.bg_color = "#F4F6F9"
        self.primary_color = "#4361EE"
        
        # Limpiar contenedor principal
        for widget in self.container.winfo_children(): 
            widget.destroy()

        self._configurar_estilos()
        self._construir_interfaz()
        self.cargar_datos()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#E2E8F0", foreground="#1E293B")
        style.map("Treeview", background=[("selected", "#EFF6FF")], foreground=[("selected", "#1D4ED8")])

    def _construir_interfaz(self):
        # Header
        header = tk.Frame(self.container, bg=self.bg_color)
        header.pack(fill="x", padx=40, pady=(30, 20))
        tk.Label(header, text="Gestión de Categorías", font=("Segoe UI", 24, "bold"), bg=self.bg_color, fg="#111827").pack(anchor="w")
        tk.Label(header, text="Administra las clasificaciones de tu inventario.", font=("Segoe UI", 11), bg=self.bg_color, fg="#64748B").pack(anchor="w")

        # Action Bar (Botones)
        action_bar = tk.Frame(self.container, bg=self.bg_color)
        action_bar.pack(fill="x", padx=40, pady=(0, 15))

        tk.Button(action_bar, text="+ Añadir Categoría", command=self.abrir_formulario, bg=self.primary_color, fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=8, cursor="hand2").pack(side="left")
        tk.Button(action_bar, text="✏️ Editar", command=lambda: self.abrir_formulario(editar=True), bg="white", fg="#475569", font=("Segoe UI", 10, "bold"), bd=1, relief="solid", padx=15, pady=8, cursor="hand2").pack(side="left", padx=10)
        tk.Button(action_bar, text="🗑️ Eliminar", command=self.eliminar_categoria, bg="#FEE2E2", fg="#EF4444", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=8, cursor="hand2").pack(side="left")

        # Tabla
        tabla_frame = tk.Frame(self.container, bg="white", bd=1, relief="solid")
        tabla_frame.pack(fill="both", expand=True, padx=40, pady=(0, 30))

        columnas = ("ID", "Nombre de la Categoría")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings")
        
        self.tabla.heading("ID", text="ID", anchor="center")
        self.tabla.heading("Nombre de la Categoría", text="Nombre de la Categoría", anchor="w")
        
        self.tabla.column("ID", width=80, anchor="center")
        self.tabla.column("Nombre de la Categoría", width=600, anchor="w")

        scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)

        self.tabla.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scroll.pack(side="right", fill="y", pady=10)

    # --- FUNCIONES DE DATOS ---
    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        for c in Categoria.obtener_todas():
            self.tabla.insert("", "end", values=(c['id_categoria'], c['nombre_categoria']))

    def abrir_formulario(self, editar=False):
        if editar and not self.tabla.selection():
            return messagebox.showwarning("Aviso", "Selecciona una categoría de la tabla para editar.")

        self.form = tk.Toplevel(self.container)
        self.form.geometry("400x200")
        self.form.title("Categoría")
        self.form.config(bg="white")
        self.form.grab_set() # Bloquea la ventana de atrás
        self.form.resizable(False, False)

        c_id = ""
        c_nom = ""

        if editar:
            item = self.tabla.selection()[0]
            val = self.tabla.item(item)['values']
            c_id = val[0]
            c_nom = val[1]

        tk.Label(self.form, text="Nueva Categoría" if not editar else "Editar Categoría", font=("Segoe UI", 14, "bold"), bg="white", fg="#111827").pack(pady=(20, 10))

        self.en_nom = tk.Entry(self.form, font=("Segoe UI", 11), bg="#F8FAFC", bd=1, relief="solid", width=35)
        self.en_nom.insert(0, c_nom)
        self.en_nom.pack(pady=10, ipady=5)

        cmd = lambda: self.guardar_categoria(editar, c_id)
        tk.Button(self.form, text="Guardar", command=cmd, bg=self.primary_color, fg="white", bd=0, font=("Segoe UI", 10, "bold"), padx=20, pady=5).pack()

    def guardar_categoria(self, editar, c_id):
        nombre = self.en_nom.get().strip()
        if not nombre:
            return messagebox.showerror("Error", "El nombre de la categoría no puede estar vacío.")

        if editar:
            exito = Categoria.actualizar(c_id, nombre)
        else:
            exito = Categoria.insertar(nombre)

        if exito:
            self.form.destroy()
            self.cargar_datos()
            messagebox.showinfo("Éxito", "Categoría guardada correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo guardar la categoría.")

    def eliminar_categoria(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return messagebox.showwarning("Aviso", "Selecciona una categoría de la tabla.")

        item = seleccion[0]
        c_id = self.tabla.item(item)['values'][0]
        c_nom = self.tabla.item(item)['values'][1]

        if messagebox.askyesno("Confirmar", f"¿Seguro que deseas eliminar la categoría '{c_nom}'?"):
            if Categoria.eliminar(c_id):
                self.cargar_datos()
                messagebox.showinfo("Éxito", "Categoría eliminada.")
            else:
                # AQUÍ ESTÁ LA PROTECCIÓN: Si tiene productos, falla el delete en MySQL y cae aquí
                messagebox.showerror("Acción Denegada", f"No se puede eliminar la categoría '{c_nom}'.\n\nTiene productos asignados en el inventario. Cambia los productos de categoría primero.")