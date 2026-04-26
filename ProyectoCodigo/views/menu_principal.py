import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config.db_conexion import ConexionDB

class MenuPrincipal:
    def __init__(self, root, usuario, logout_callback):
        self.root = root
        self.usuario = usuario
        self.logout_callback = logout_callback
        self.db = ConexionDB()

        self.root.title(f"Smart Sales | Usuario: {self.usuario.get('nombre', 'Admin')}")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        self.root.config(bg="#F4F6F9")

        for widget in root.winfo_children():
            widget.destroy()

        # Paleta de colores
        self.bg_sidebar   = "#FFFFFF"
        self.bg_content   = "#F4F6F9"
        self.color_texto  = "#333333"
        self.color_hover  = "#E2E8F0"
        self.color_activo = "#4361EE"
        self.texto_activo = "#FFFFFF"

        # Estructura principal
        self.sidebar = tk.Frame(self.root, bg=self.bg_sidebar, width=250,
                                highlightbackground="#E2E8F0", highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content_frame = tk.Frame(self.root, bg=self.bg_content)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self._construir_sidebar()
        self.abrir_dashboard()

    # SIDEBAR

    def _construir_sidebar(self):
        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=self.bg_sidebar)
        logo_frame.pack(fill="x", pady=20)
        tk.Label(logo_frame, text="📦 SMART", font=("Segoe UI", 18, "bold"),
                 bg=self.bg_sidebar, fg=self.color_activo).pack(side="left", padx=(20, 5))
        tk.Label(logo_frame, text="KARDEX", font=("Segoe UI", 18),
                 bg=self.bg_sidebar, fg=self.color_texto).pack(side="left")

        tk.Frame(self.sidebar, bg="#E2E8F0", height=1).pack(fill="x", padx=20, pady=10)

        self.botones = {}

        # Módulos principales (todos los usuarios)
        modulos = [
            ("📊", "Dashboard",    self.abrir_dashboard),
            ("🏷️", "Productos",    self.abrir_productos),
            ("📂", "Categorías",   self.abrir_categorias),
            ("🔄", "Movimientos",  self.abrir_movimientos),
            ("⚠️", "Alertas",      self.abrir_alertas),
            ("🏢", "Proveedores",  self.abrir_proveedores),
        ]

        for icono, texto, comando in modulos:
            btn = self._crear_boton_menu(icono, texto, comando)
            btn.pack(fill="x", padx=10, pady=2)
            self.botones[texto] = btn

        # Empujar sección inferior
        tk.Frame(self.sidebar, bg=self.bg_sidebar).pack(fill="both", expand=True)
        tk.Frame(self.sidebar, bg="#E2E8F0", height=1).pack(fill="x", padx=20, pady=10)

        # Módulos solo para ADMIN
        if self.usuario.get("rol") == "ADMIN":
            for icono, texto, comando in [
                ("👥", "Usuarios",       self.abrir_usuarios),
                ("⚙️", "Configuración",  self.abrir_configuracion),
            ]:
                btn = self._crear_boton_menu(icono, texto, comando)
                btn.pack(fill="x", padx=10, pady=2)
                self.botones[texto] = btn

        # Cerrar sesión
        btn_salir = self._crear_boton_menu("🚪", "Cerrar Sesión",
                                           self.logout_callback, fg_color="#E63946")
        btn_salir.pack(fill="x", padx=10, pady=(2, 20))

    def _crear_boton_menu(self, icono, texto, comando, fg_color=None):
        color_fuente = fg_color if fg_color else self.color_texto
        btn = tk.Button(
            self.sidebar,
            text=f"  {icono}   {texto}", anchor="w",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_sidebar, fg=color_fuente,
            bd=0, relief="flat", cursor="hand2",
            command=lambda t=texto, c=comando: self._seleccionar_menu(t, c),
            activebackground=self.color_hover,
            padx=20, pady=10
        )
        btn.bind("<Enter>", lambda e, b=btn, c=color_fuente: self._on_enter(b, c))
        btn.bind("<Leave>", lambda e, b=btn, c=color_fuente: self._on_leave(b, c))
        return btn

    def _on_enter(self, btn, base_fg):
        if btn.cget("bg") != self.color_activo:
            btn.config(bg=self.color_hover)

    def _on_leave(self, btn, base_fg):
        if btn.cget("bg") != self.color_activo:
            btn.config(bg=self.bg_sidebar, fg=base_fg)

    def _seleccionar_menu(self, texto_modulo, comando):
        for nombre, btn in self.botones.items():
            color_original = "#E63946" if nombre == "Cerrar Sesión" else self.color_texto
            btn.config(bg=self.bg_sidebar, fg=color_original)

        if texto_modulo in self.botones and texto_modulo != "Cerrar Sesión":
            self.botones[texto_modulo].config(bg=self.color_activo, fg=self.texto_activo)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        comando()

    # DASHBOARD

    def abrir_dashboard(self):
        header = tk.Frame(self.content_frame, bg=self.bg_content)
        header.pack(fill="x", padx=30, pady=(30, 10))

        tk.Label(header, text="Dashboard Principal", font=("Segoe UI", 20, "bold"),
                 bg=self.bg_content, fg="#1E293B").pack(side="left")

        combo_fecha = ttk.Combobox(header, values=["Hoy", "Esta Semana", "Este Mes", "Este Año"],
                                   state="readonly", width=15)
        combo_fecha.set("Este Mes")
        combo_fecha.pack(side="right", pady=5)
        tk.Label(header, text="Filtrar por:", bg=self.bg_content,
                 font=("Segoe UI", 10)).pack(side="right", padx=10)

        cards_frame = tk.Frame(self.content_frame, bg=self.bg_content)
        cards_frame.pack(fill="x", padx=30, pady=10)
        self._render_cards(cards_frame)

        chart_frame = tk.Frame(self.content_frame, bg="#FFFFFF", bd=0,
                               highlightbackground="#E2E8F0", highlightthickness=1)
        chart_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self._render_chart(chart_frame)

    def _crear_tarjeta(self, parent, titulo, valor, icono, color_palo):
        card = tk.Frame(parent, bg="#FFFFFF", padx=20, pady=20,
                        highlightbackground="#E2E8F0", highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=5)

        palo = tk.Frame(card, bg=color_palo, width=4)
        palo.place(relx=0, rely=0, relheight=1)

        tk.Label(card, text=icono,  font=("Segoe UI", 20), bg="#FFFFFF").pack(anchor="w")
        tk.Label(card, text=titulo, font=("Segoe UI", 10), bg="#FFFFFF", fg="#64748B").pack(anchor="w", pady=(5, 0))
        tk.Label(card, text=valor,  font=("Segoe UI", 16, "bold"), bg="#FFFFFF", fg="#1E293B").pack(anchor="w")

    def _render_cards(self, cards_frame):
        cursor = self.db.obtener_cursor()
        valor_total = 0.0; alertas = 0; total_p = 0; movs = 0

        if cursor:
            try:
                cursor.execute("SELECT COUNT(*) as total FROM productos WHERE stock <= stock_minimo")
                res = cursor.fetchone()
                if res: alertas = res["total"]

                cursor.execute("SELECT COUNT(*) as total, SUM(costo * stock) as valor_total FROM productos")
                res = cursor.fetchone()
                if res:
                    total_p     = res["total"] or 0
                    valor_total = res["valor_total"] or 0.0

                cursor.execute("SELECT COUNT(*) as total FROM movimientos_inventario WHERE MONTH(fecha)=MONTH(CURRENT_DATE())")
                res = cursor.fetchone()
                if res: movs = res["total"]
            except Exception as e:
                print("Dashboard cards:", e)

        self._crear_tarjeta(cards_frame, "Valor Inventario", f"${valor_total:,.2f}", "💰", "#10B981")
        self._crear_tarjeta(cards_frame, "Alertas Stock",    str(alertas),            "⚠️",  "#EF4444")
        self._crear_tarjeta(cards_frame, "Total Productos",  str(total_p),            "📦", "#4361EE")
        self._crear_tarjeta(cards_frame, "Movs. del Mes",    str(movs),               "🔄", "#F59E0B")

    def _render_chart(self, chart_frame):
        cursor = self.db.obtener_cursor()
        entradas   = [0] * 5
        salidas    = [0] * 5
        categorias = ["Mes 1", "Mes 2", "Mes 3", "Mes 4", "Mes Actual"]

        if cursor:
            try:
                sql = """
                    SELECT MONTH(fecha) AS mes, tipo_movimiento, SUM(cantidad) AS total
                    FROM movimientos_inventario
                    WHERE fecha >= DATE_SUB(CURRENT_DATE(), INTERVAL 5 MONTH)
                    GROUP BY MONTH(fecha), tipo_movimiento
                    ORDER BY MONTH(fecha) ASC
                """
                cursor.execute(sql)
                resultados = cursor.fetchall()

                if resultados:
                    meses_encontrados = []
                    for row in resultados:
                        if row["mes"] not in meses_encontrados:
                            meses_encontrados.append(row["mes"])

                    nombres = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                               7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
                    categorias = [nombres.get(m, str(m)) for m in meses_encontrados]
                    entradas   = [0] * len(meses_encontrados)
                    salidas    = [0] * len(meses_encontrados)

                    for row in resultados:
                        idx = meses_encontrados.index(row["mes"])
                        if row["tipo_movimiento"] == "ENTRADA":
                            entradas[idx] = int(row["total"])
                        else:
                            salidas[idx]  = int(row["total"])
            except Exception as e:
                print("Dashboard chart:", e)

        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor("#FFFFFF")
        width     = 0.35
        x_indices = range(len(categorias)) if categorias else range(5)

        ax.bar([i - width/2 for i in x_indices], entradas, width, label="Entradas", color="#4361EE", edgecolor="white")
        ax.bar([i + width/2 for i in x_indices], salidas,  width, label="Salidas",  color="#E63946", edgecolor="white")

        ax.set_title("Flujo de Inventario Mensual", fontsize=12, pad=20,
                     fontweight="bold", color="#1E293B")
        ax.set_xticks(x_indices)
        ax.set_xticklabels(categorias)
        ax.legend(frameon=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_facecolor("#FFFFFF")

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    # NAVEGACIÓN A MÓDULOS

    def abrir_productos(self):
        from views.productos_view import VentanaProductos
        VentanaProductos(self.content_frame)

    def abrir_movimientos(self):
        from views.movimientos_view import VentanaMovimientos
        VentanaMovimientos(self.content_frame)

    def abrir_alertas(self):
        from views.alertas_view import VentanaAlertas
        VentanaAlertas(self.content_frame)

    def abrir_proveedores(self):
        from views.proveedores_view import VentanaProveedores
        VentanaProveedores(self.content_frame)

    def abrir_usuarios(self):
        """Solo ADMIN — ya está protegido desde el sidebar."""
        from views.usuarios_view import VentanaUsuarios
        VentanaUsuarios(self.content_frame, self.usuario)

    def abrir_configuracion(self):
        from views.config_view import VentanaConfig
        VentanaConfig(self.content_frame, lambda: self._seleccionar_menu("Dashboard", self.abrir_dashboard))
    
    def abrir_categorias(self):
        from views.categorias_view import VentanaCategorias
        VentanaCategorias(self.content_frame)