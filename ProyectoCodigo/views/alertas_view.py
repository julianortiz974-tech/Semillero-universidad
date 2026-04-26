import tkinter as tk
from tkinter import ttk, messagebox
from models.modelos import Producto
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VentanaAlertas:
    def __init__(self, container):
        self.container = container
        self.bg_color  = "#F4F6F9"
        self._productos_alerta = []   # Cache para la orden de compra

        for widget in self.container.winfo_children():
            widget.destroy()

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

        titulo_frame = tk.Frame(header, bg=self.bg_color)
        titulo_frame.pack(side="left")
        tk.Label(titulo_frame, text="⚠️ Alertas de Stock",
                 font=("Segoe UI", 24, "bold"),
                 bg=self.bg_color, fg="#111827").pack(anchor="w")
        tk.Label(titulo_frame, text="Productos que requieren reabastecimiento urgente.",
                 font=("Segoe UI", 11), bg=self.bg_color, fg="#64748B").pack(anchor="w")

        tk.Button(header, text="🛒  Generar Orden de Compra",
                  command=self.generar_orden,
                  bg="#4361EE", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"),
                  padx=15, pady=8, cursor="hand2",
                  activebackground="#2b4fd4"
                  ).pack(side="right")

        # CUERPO
        main_content = tk.Frame(self.container, bg=self.bg_color)
        main_content.pack(fill="both", expand=True, padx=40, pady=(10, 30))

        # Panel izquierdo: gráfica de dona
        self.panel_izq = tk.Frame(main_content, bg="white", bd=1,
                                   relief="solid", width=300)
        self.panel_izq.pack(side="left", fill="y", padx=(0, 20))
        self.panel_izq.pack_propagate(False)

        tk.Label(self.panel_izq, text="Estado General del Inventario",
                 font=("Segoe UI", 12, "bold"),
                 bg="white", fg="#1E293B", pady=15).pack()
        self.chart_frame = tk.Frame(self.panel_izq, bg="white")
        self.chart_frame.pack(fill="both", expand=True)

        # Panel derecho: tabla
        panel_der = tk.Frame(main_content, bg=self.bg_color)
        panel_der.pack(side="right", fill="both", expand=True)

        table_frame = tk.Frame(panel_der, bg="white", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True)

        columnas = ("ID", "Producto", "Categoría",
                    "Stock Actual", "Mínimo Requerido", "Estado")
        self.tabla = ttk.Treeview(table_frame, columns=columnas, show="headings")

        anchos = {"ID": 40, "Producto": 250, "Categoría": 150,
                  "Stock Actual": 100, "Mínimo Requerido": 120, "Estado": 110}
        for col in columnas:
            self.tabla.heading(col, text=col.upper())
            self.tabla.column(col, anchor="center", width=anchos[col])

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tabla.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.tabla.tag_configure("agotado", background="#FEF2F2", foreground="#991B1B")
        self.tabla.tag_configure("bajo",    background="#FFFBEB", foreground="#B45309")

        self.cargar_datos_y_grafica()

    def cargar_datos_y_grafica(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self._productos_alerta = []
        productos = Producto.obtener_todos()
        optimos = bajos = agotados = 0

        for p in productos:
            stock  = int(p["stock"])
            minimo = int(p["stock_minimo"])

            if stock == 0:
                agotados += 1
                tag = "agotado"
                estado = "❌ AGOTADO"
                self._productos_alerta.append(p)
                self.tabla.insert("", "end", values=(
                    p["id_producto"], p["nombre"],
                    p["nombre_categoria"] or "—",
                    stock, minimo, estado
                ), tags=(tag,))
            elif stock <= minimo:
                bajos += 1
                tag = "bajo"
                estado = "⚠️ BAJO STOCK"
                self._productos_alerta.append(p)
                self.tabla.insert("", "end", values=(
                    p["id_producto"], p["nombre"],
                    p["nombre_categoria"] or "—",
                    stock, minimo, estado
                ), tags=(tag,))
            else:
                optimos += 1

        self._dibujar_dona(optimos, bajos, agotados)

    def _dibujar_dona(self, optimos, bajos, agotados):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if optimos == 0 and bajos == 0 and agotados == 0:
            tk.Label(self.chart_frame, text="No hay datos de productos.",
                     bg="white", fg="gray").pack(pady=50)
            return

        fig, ax = plt.subplots(figsize=(3, 3), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")

        valores   = [optimos, bajos, agotados]
        etiquetas = ["Óptimo", "Bajo", "Agotado"]
        colores   = ["#10B981", "#F59E0B", "#EF4444"]

        v_f, c_f, e_f = [], [], []
        for v, c, e in zip(valores, colores, etiquetas):
            if v > 0:
                v_f.append(v); c_f.append(c); e_f.append(e)

        wedges, _ = ax.pie(v_f, colors=c_f, startangle=90,
                           wedgeprops=dict(width=0.4, edgecolor="white"))
        ax.legend(wedges, e_f, title="Estado", loc="center",
                  bbox_to_anchor=(0.5, -0.1), frameon=False)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=(20, 0))
        plt.close(fig)

    def generar_orden(self):
        if not self._productos_alerta:
            messagebox.showinfo("Sin alertas",
                "Todos los productos tienen stock óptimo. "
                "No es necesaria una orden de compra.")
            return
        from reportes import generar_orden_compra
        generar_orden_compra(self._productos_alerta)