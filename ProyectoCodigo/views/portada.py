import tkinter as tk
from tkinter import font as tkfont


# ── Paleta ───────────────────────────────────────────────────────────────────
BG          = "#F8FAFF"        # Fondo general blanco-azulado
AZUL        = "#4361EE"        # Azul principal
AZUL_DARK   = "#2b4fd4"        # Hover botón
AZUL_LITE   = "#EEF2FF"        # Fondo suave azul
TEXTO       = "#0F172A"        # Texto oscuro
TEXTO_MID   = "#475569"        # Texto secundario
TEXTO_LITE  = "#94A3B8"        # Texto débil
VERDE       = "#10B981"        # Acento verde
NARANJA     = "#F59E0B"        # Acento naranja
ROJO        = "#EF4444"        # Acento rojo
BLANCO      = "#FFFFFF"
BORDE       = "#E2E8F0"


class VentanaPortada:
    def __init__(self, root, callback_login):
        self.root           = root
        self.callback_login = callback_login

        for w in root.winfo_children():
            w.destroy()

        root.configure(bg=BG)
        root.title("SmartKardex — Control total de tu inventario")

        self._construir()

    # ──────────────────────────────────────────────────────────────────────
    # CONSTRUCCIÓN
    # ──────────────────────────────────────────────────────────────────────

    def _construir(self):
        # ── NAVBAR ────────────────────────────────────────────────────────
        nav = tk.Frame(self.root, bg=BLANCO, height=64,
                       highlightbackground=BORDE, highlightthickness=1)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        nav_inner = tk.Frame(nav, bg=BLANCO)
        nav_inner.pack(fill="both", expand=True, padx=50)

        # Logo
        logo_f = tk.Frame(nav_inner, bg=BLANCO)
        logo_f.pack(side="left", pady=14)
        tk.Label(logo_f, text="📦", font=("Segoe UI", 18),
                 bg=BLANCO).pack(side="left")
        tk.Label(logo_f, text=" Smart", font=("Segoe UI", 15, "bold"),
                 bg=BLANCO, fg=TEXTO).pack(side="left")
        tk.Label(logo_f, text="Kardex", font=("Segoe UI", 15, "bold"),
                 bg=BLANCO, fg=AZUL).pack(side="left")

        # Botón iniciar sesión
        btn_nav = tk.Button(
            nav_inner, text="Iniciar sesión →",
            command=self.callback_login,
            bg=AZUL, fg=BLANCO, relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2", padx=20, pady=6,
            activebackground=AZUL_DARK, activeforeground=BLANCO
        )
        btn_nav.pack(side="right", pady=14)
        btn_nav.bind("<Enter>", lambda e: btn_nav.config(bg=AZUL_DARK))
        btn_nav.bind("<Leave>", lambda e: btn_nav.config(bg=AZUL))

        # ── SCROLL CONTAINER ──────────────────────────────────────────────
        canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        page = tk.Frame(canvas, bg=BG)
        win  = canvas.create_window((0, 0), window=page, anchor="nw")

        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win, width=e.width))
        page.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        def _scroll(event):
            try:
                canvas.yview_scroll(-1*(event.delta//120), "units")
            except Exception:
                pass

        canvas.bind_all("<MouseWheel>", _scroll)
        canvas.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # ── HERO ──────────────────────────────────────────────────────────
        self._hero(page)

        # ── DASHBOARD MOCKUP ──────────────────────────────────────────────
        self._mockup(page)

        # ── CARACTERÍSTICAS ───────────────────────────────────────────────
        self._caracteristicas(page)

        # ── BENEFICIOS ────────────────────────────────────────────────────
        self._beneficios(page)

        # ── CTA FINAL ─────────────────────────────────────────────────────
        self._cta_final(page)

        # ── FOOTER ────────────────────────────────────────────────────────
        self._footer(page)

    # ──────────────────────────────────────────────────────────────────────
    # SECCIONES
    # ──────────────────────────────────────────────────────────────────────

    def _hero(self, parent):
        hero = tk.Frame(parent, bg=BG)
        hero.pack(fill="x", padx=80, pady=(60, 20))

        # Badge
        badge_f = tk.Frame(hero, bg=AZUL_LITE, padx=12, pady=4)
        badge_f.pack(anchor="center")
        tk.Label(badge_f, text="✦  Solución completa para tu inventario",
                 font=("Segoe UI", 10), bg=AZUL_LITE, fg=AZUL).pack()

        # Título principal
        tk.Label(hero,
                 text="Control total de tu",
                 font=("Segoe UI", 42, "bold"),
                 bg=BG, fg=TEXTO,
                 justify="center").pack(pady=(20, 0))

        titulo2 = tk.Label(hero, text="inventario, en tiempo real",
                           font=("Segoe UI", 42, "bold"),
                           bg=BG, fg=AZUL, justify="center")
        titulo2.pack()

        # Subtítulo
        tk.Label(hero,
                 text="SmartKardex es el sistema que te permite gestionar tus productos,\n"
                      "stock, proveedores y movimientos de forma eficiente, fácil y segura.",
                 font=("Segoe UI", 13), bg=BG, fg=TEXTO_MID,
                 justify="center").pack(pady=(16, 32))

        # Botones CTA
        btns = tk.Frame(hero, bg=BG)
        btns.pack()

        btn_main = tk.Button(
            btns, text="  Comenzar ahora  →",
            command=self.callback_login,
            bg=AZUL, fg=BLANCO, relief="flat",
            font=("Segoe UI", 13, "bold"),
            cursor="hand2", padx=30, pady=12,
            activebackground=AZUL_DARK, activeforeground=BLANCO
        )
        btn_main.pack(side="left", padx=(0, 12))
        btn_main.bind("<Enter>", lambda e: btn_main.config(bg=AZUL_DARK))
        btn_main.bind("<Leave>", lambda e: btn_main.config(bg=AZUL))

        btn_sec = tk.Button(
            btns, text="▶  Ver cómo funciona",
            command=self._mostrar_caracteristicas,
            bg=BLANCO, fg=TEXTO, relief="flat",
            font=("Segoe UI", 13),
            cursor="hand2", padx=24, pady=12,
            highlightbackground=BORDE, highlightthickness=1,
            activebackground=AZUL_LITE
        )
        btn_sec.pack(side="left")

        # Mini badges de confianza
        trust = tk.Frame(hero, bg=BG)
        trust.pack(pady=(28, 0))
        for icono, txt in [("✓", "Fácil de usar"),
                           ("🔒", "Datos seguros"),
                           ("⚡", "Rápido y eficiente")]:
            f = tk.Frame(trust, bg=BG)
            f.pack(side="left", padx=20)
            tk.Label(f, text=icono, font=("Segoe UI", 12),
                     bg=BG, fg=AZUL).pack(side="left")
            tk.Label(f, text=f"  {txt}", font=("Segoe UI", 10),
                     bg=BG, fg=TEXTO_MID).pack(side="left")

    def _mockup(self, parent):
        """Simulación del dashboard dentro de un 'navegador'."""
        outer = tk.Frame(parent, bg=BG)
        outer.pack(padx=100, pady=(20, 50))

        # Sombra / contenedor
        container = tk.Frame(outer, bg=BORDE, padx=2, pady=2)
        container.pack()

        win_frame = tk.Frame(container, bg=BLANCO)
        win_frame.pack()

        # Barra de ventana
        win_bar = tk.Frame(win_frame, bg="#E2E8F0", height=32)
        win_bar.pack(fill="x")
        for color in ["#EF4444", "#F59E0B", "#10B981"]:
            tk.Frame(win_bar, bg=color, width=12, height=12).pack(
                side="left", padx=(8, 2), pady=10)
        tk.Label(win_bar, text="SmartKardex — Dashboard",
                 font=("Segoe UI", 9), bg="#E2E8F0", fg=TEXTO_MID).pack(
                 side="left", padx=12)

        # Contenido mockup
        mock = tk.Frame(win_frame, bg=BG, width=900, height=380)
        mock.pack()
        mock.pack_propagate(False)

        # Sidebar simulado
        sidebar = tk.Frame(mock, bg=BLANCO, width=160,
                           highlightbackground=BORDE, highlightthickness=1)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="📦 SmartKardex",
                 font=("Segoe UI", 9, "bold"),
                 bg=BLANCO, fg=AZUL).pack(pady=(12, 8), padx=8, anchor="w")

        for icono, txt, activo in [
            ("📊", "Dashboard",   True),
            ("🏷️", "Productos",  False),
            ("🔄", "Movimientos", False),
            ("⚠️", "Alertas",    False),
            ("🏢", "Proveedores", False),
        ]:
            bg_btn = AZUL if activo else BLANCO
            fg_btn = BLANCO if activo else TEXTO_MID
            tk.Label(sidebar, text=f"  {icono}  {txt}",
                     font=("Segoe UI", 9, "bold" if activo else "normal"),
                     bg=bg_btn, fg=fg_btn,
                     anchor="w", padx=8, pady=6).pack(
                     fill="x", padx=6, pady=1)

        # Área de contenido
        content = tk.Frame(mock, bg=BG)
        content.pack(side="left", fill="both", expand=True, padx=16, pady=12)

        tk.Label(content, text="Dashboard",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG, fg=TEXTO).pack(anchor="w")

        # Tarjetas de métricas
        cards_row = tk.Frame(content, bg=BG)
        cards_row.pack(fill="x", pady=(10, 0))

        metricas = [
            ("Productos totales", "1,256", AZUL,    "📦"),
            ("Stock total",       "8,452", VERDE,   "📊"),
            ("Movimientos hoy",   "32",    NARANJA, "🔄"),
            ("Valor inventario",  "$245K", "#7C3AED","💰"),
        ]
        for titulo, valor, color, ico in metricas:
            card = tk.Frame(cards_row, bg=BLANCO,
                            highlightbackground=BORDE, highlightthickness=1,
                            padx=12, pady=10)
            card.pack(side="left", expand=True, fill="x", padx=(0, 8))
            tk.Label(card, text=ico, font=("Segoe UI", 14),
                     bg=BLANCO).pack(anchor="w")
            tk.Label(card, text=titulo, font=("Segoe UI", 8),
                     bg=BLANCO, fg=TEXTO_LITE).pack(anchor="w")
            tk.Label(card, text=valor, font=("Segoe UI", 13, "bold"),
                     bg=BLANCO, fg=color).pack(anchor="w")

        # Fila inferior mockup
        bot = tk.Frame(content, bg=BG)
        bot.pack(fill="both", expand=True, pady=(10, 0))

        # Tabla simulada
        tabla_f = tk.Frame(bot, bg=BLANCO,
                           highlightbackground=BORDE, highlightthickness=1)
        tabla_f.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(tabla_f, text="Productos más vendidos",
                 font=("Segoe UI", 9, "bold"),
                 bg=BLANCO, fg=TEXTO, padx=10).pack(anchor="w", pady=(8, 4))

        for i, (prod, cant) in enumerate([
            ("Auriculares Bluetooth", "320 und"),
            ("Teclado Inalámbrico",   "280 und"),
            ("Mouse Óptico",          "210 und"),
            ("Monitor 24\"",          "180 und"),
        ]):
            row_bg = "#F8FAFF" if i % 2 == 0 else BLANCO
            row = tk.Frame(tabla_f, bg=row_bg)
            row.pack(fill="x", padx=8, pady=1)
            tk.Label(row, text=f"{i+1}. {prod}",
                     font=("Segoe UI", 8), bg=row_bg,
                     fg=TEXTO_MID).pack(side="left", padx=4, pady=3)
            tk.Label(row, text=cant,
                     font=("Segoe UI", 8), bg=row_bg,
                     fg=TEXTO_LITE).pack(side="right", padx=4)

        # Alertas simuladas
        alertas_f = tk.Frame(bot, bg=BLANCO, width=200,
                              highlightbackground=BORDE, highlightthickness=1)
        alertas_f.pack(side="right", fill="y")
        alertas_f.pack_propagate(False)

        tk.Label(alertas_f, text="Alertas de inventario",
                 font=("Segoe UI", 9, "bold"),
                 bg=BLANCO, fg=TEXTO, padx=10).pack(anchor="w", pady=(8, 4))

        for txt, sub, color in [
            ("5 productos con stock bajo", "Revisa el inventario mínimo.", "#FEF2F2"),
            ("2 productos sin stock",      "Gestiona la reposición.",      "#FEF2F2"),
        ]:
            a = tk.Frame(alertas_f, bg=color, padx=8, pady=6)
            a.pack(fill="x", padx=6, pady=3)
            tk.Label(a, text=f"⚠ {txt}",
                     font=("Segoe UI", 8, "bold"),
                     bg=color, fg="#991B1B",
                     wraplength=160, justify="left").pack(anchor="w")
            tk.Label(a, text=sub,
                     font=("Segoe UI", 7),
                     bg=color, fg="#B91C1C",
                     wraplength=160, justify="left").pack(anchor="w")

    def _caracteristicas(self, parent):
        sec = tk.Frame(parent, bg=BLANCO,
                       highlightbackground=BORDE, highlightthickness=1)
        sec.pack(fill="x", padx=60, pady=(0, 50))

        tk.Label(sec, text="Todo lo que necesitas para tu negocio",
                 font=("Segoe UI", 22, "bold"),
                 bg=BLANCO, fg=TEXTO).pack(pady=(40, 8))
        tk.Label(sec,
                 text="Funcionalidades diseñadas para que tengas el control completo de tu inventario.",
                 font=("Segoe UI", 11), bg=BLANCO, fg=TEXTO_MID).pack()

        cards = tk.Frame(sec, bg=BLANCO)
        cards.pack(fill="x", padx=40, pady=(30, 40))

        features = [
            ("📦", "Inventario Inteligente",
             "Gestiona productos, categorías y stock en tiempo real con alertas automáticas."),
            ("🔄", "Movimientos Kardex",
             "Registra entradas y salidas con historial completo y reportes en PDF."),
            ("⚠️", "Alertas de Stock",
             "Detecta productos con stock bajo o agotado y genera órdenes de compra."),
            ("📊", "Dashboard Visual",
             "Visualiza el estado de tu inventario con gráficas y métricas en tiempo real."),
            ("🏢", "Gestión de Proveedores",
             "Administra tus proveedores y genera órdenes de compra profesionales."),
            ("👥", "Control de Usuarios",
             "Asigna roles y permisos. Administradores y cajeros con accesos diferenciados."),
        ]

        for i, (ico, titulo, desc) in enumerate(features):
            col = i % 3
            row = i // 3

            card = tk.Frame(cards, bg=BG,
                            highlightbackground=BORDE, highlightthickness=1,
                            padx=20, pady=20)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            cards.columnconfigure(col, weight=1)

            ico_f = tk.Frame(card, bg=AZUL_LITE, width=44, height=44)
            ico_f.pack(anchor="w")
            ico_f.pack_propagate(False)
            tk.Label(ico_f, text=ico, font=("Segoe UI", 18),
                     bg=AZUL_LITE).place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(card, text=titulo,
                     font=("Segoe UI", 11, "bold"),
                     bg=BG, fg=TEXTO).pack(anchor="w", pady=(10, 4))
            tk.Label(card, text=desc,
                     font=("Segoe UI", 9), bg=BG, fg=TEXTO_MID,
                     wraplength=220, justify="left").pack(anchor="w")

    def _beneficios(self, parent):
        sec = tk.Frame(parent, bg=BG)
        sec.pack(fill="x", padx=60, pady=(0, 50))

        tk.Label(sec, text="¿Por qué elegir SmartKardex?",
                 font=("Segoe UI", 22, "bold"),
                 bg=BG, fg=TEXTO).pack(pady=(0, 30))

        row = tk.Frame(sec, bg=BG)
        row.pack(fill="x")

        beneficios = [
            ("✓", "Fácil de usar",
             "Interfaz intuitiva que no requiere capacitación extensa.", VERDE),
            ("🔒", "Datos seguros",
             "Contraseñas cifradas con SHA-256 y respaldo de base de datos.", AZUL),
            ("⚡", "Rápido y eficiente",
             "Accede a toda tu información en segundos, sin demoras.", NARANJA),
            ("📄", "Reportes PDF",
             "Genera Kardex y Órdenes de Compra profesionales con un clic.", "#7C3AED"),
        ]

        for ico, titulo, desc, color in beneficios:
            card = tk.Frame(row, bg=BLANCO,
                            highlightbackground=BORDE, highlightthickness=1,
                            padx=20, pady=24)
            card.pack(side="left", expand=True, fill="both", padx=6)

            top = tk.Frame(card, bg=BLANCO)
            top.pack(anchor="w")

            circle = tk.Frame(top, bg=color, width=36, height=36)
            circle.pack(side="left")
            circle.pack_propagate(False)
            tk.Label(circle, text=ico, font=("Segoe UI", 14),
                     bg=color, fg=BLANCO).place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(top, text=f"  {titulo}",
                     font=("Segoe UI", 11, "bold"),
                     bg=BLANCO, fg=TEXTO).pack(side="left")

            tk.Label(card, text=desc,
                     font=("Segoe UI", 9), bg=BLANCO, fg=TEXTO_MID,
                     wraplength=200, justify="left").pack(anchor="w", pady=(8, 0))

    def _cta_final(self, parent):
        sec = tk.Frame(parent, bg=AZUL)
        sec.pack(fill="x", padx=0, pady=(0, 0))

        tk.Label(sec, text="¿Listo para tomar el control?",
                 font=("Segoe UI", 24, "bold"),
                 bg=AZUL, fg=BLANCO).pack(pady=(50, 8))
        tk.Label(sec,
                 text="Accede ahora y empieza a gestionar tu inventario de forma profesional.",
                 font=("Segoe UI", 12), bg=AZUL, fg="#BFD3FF").pack()

        btn = tk.Button(
            sec, text="  Iniciar sesión  →",
            command=self.callback_login,
            bg=BLANCO, fg=AZUL, relief="flat",
            font=("Segoe UI", 13, "bold"),
            cursor="hand2", padx=32, pady=12,
            activebackground=AZUL_LITE, activeforeground=AZUL_DARK
        )
        btn.pack(pady=(24, 50))
        btn.bind("<Enter>", lambda e: btn.config(bg=AZUL_LITE))
        btn.bind("<Leave>", lambda e: btn.config(bg=BLANCO))

    def _footer(self, parent):
        footer = tk.Frame(parent, bg="#0F172A", height=60)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        tk.Label(footer,
                 text="© 2026 SmartKardex  ·  Sistema de Inventario  ·  Todos los derechos reservados",
                 font=("Segoe UI", 9),
                 bg="#0F172A", fg="#475569").pack(expand=True)

    # ──────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────

    def _mostrar_caracteristicas(self):
        """El botón 'Ver cómo funciona' hace scroll hacia abajo."""
        # En Tkinter no hay scroll programático fácil con Canvas sin referencia,
        # así que simplemente abrimos el login también — o podríamos mostrar un msgbox
        tk.messagebox.showinfo(
            "SmartKardex",
            "📦  SmartKardex incluye:\n\n"
            "✅  Gestión de productos y categorías\n"
            "✅  Movimientos de entrada y salida (Kardex)\n"
            "✅  Alertas de stock bajo y agotado\n"
            "✅  Órdenes de compra en PDF\n"
            "✅  Dashboard con gráficas en tiempo real\n"
            "✅  Control de usuarios con roles\n"
            "✅  Respaldo de base de datos\n\n"
            "Presiona 'Comenzar ahora' para iniciar sesión."
        )