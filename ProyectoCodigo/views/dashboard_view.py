import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config.db_conexion import ConexionDB
from datetime import datetime

class DashboardView:
    def __init__(self, container):
        self.container = container
        self.db = ConexionDB()
        
        # --- Configuración de Estilo ---
        self.bg_color = "#F4F6F9"
        self.card_color = "#FFFFFF"
        self.accent_color = "#4361EE"
        
        # Título y Filtros
        self._header_dashboard()
        
        # Fila de Tarjetas (KPIs)
        self.cards_frame = tk.Frame(self.container, bg=self.bg_color)
        self.cards_frame.pack(fill="x", padx=30, pady=10)
        self._render_cards()
        
        # Área de Gráfica
        self.chart_frame = tk.Frame(self.container, bg=self.card_color, bd=0, highlightbackground="#E2E8F0", highlightthickness=1)
        self.chart_frame.pack(fill="both", expand=True, padx=30, pady=20)
        self._render_chart()

    def _header_dashboard(self):
        header = tk.Frame(self.container, bg=self.bg_color)
        header.pack(fill="x", padx=30, pady=(30, 10))
        
        tk.Label(header, text="Dashboard Principal", font=("Segoe UI", 20, "bold"), 
                 bg=self.bg_color, fg="#1E293B").pack(side="left")
        
        # Filtro de Fecha (Combobox Estilizado)
        self.combo_fecha = ttk.Combobox(header, values=["Hoy", "Esta Semana", "Este Mes", "Este Año"], state="readonly", width=15)
        self.combo_fecha.set("Este Mes")
        self.combo_fecha.pack(side="right", pady=5)
        tk.Label(header, text="Filtrar por:", bg=self.bg_color, font=("Segoe UI", 10)).pack(side="right", padx=10)

    def _crear_tarjeta(self, parent, titulo, valor, icono, color_palo):
        card = tk.Frame(parent, bg=self.card_color, padx=20, pady=20, highlightbackground="#E2E8F0", highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=5)
        
        # Barra lateral de color para resaltar
        palo = tk.Frame(card, bg=color_palo, width=4)
        palo.place(relx=0, rely=0, relheight=1)
        
        tk.Label(card, text=icono, font=("Segoe UI", 20), bg=self.card_color).pack(anchor="w")
        tk.Label(card, text=titulo, font=("Segoe UI", 10), bg=self.card_color, fg="#64748B").pack(anchor="w", pady=(5, 0))
        tk.Label(card, text=valor, font=("Segoe UI", 16, "bold"), bg=self.card_color, fg="#1E293B").pack(anchor="w")

    def _render_cards(self):
        # Consultas Reales a la DB
        cursor = self.db.obtener_cursor()
        
        # 1. Alertas de Stock
        cursor.execute("SELECT COUNT(*) as total FROM productos WHERE stock <= stock_minimo")
        alertas = cursor.fetchone()['total']
        
        # 2. Total Productos
        cursor.execute("SELECT COUNT(*) as total FROM productos")
        total_p = cursor.fetchone()['total']
        
        # 3. Movimientos del Mes
        cursor.execute("SELECT COUNT(*) as total FROM movimientos_inventario WHERE MONTH(fecha) = MONTH(CURRENT_DATE())")
        movs = cursor.fetchone()['total']

        # Renderizar Tarjetas
        self._crear_tarjeta(self.cards_frame, "Valor Inventario", "$0.00", "💰", "#10B981")
        self._crear_tarjeta(self.cards_frame, "Alertas Stock", str(alertas), "⚠️", "#EF4444")
        self._crear_tarjeta(self.cards_frame, "Total Productos", str(total_p), "📦", "#4361EE")
        self._crear_tarjeta(self.cards_frame, "Movs. del Mes", str(movs), "🔄", "#F59E0B")

    def _render_chart(self):
        # Datos de prueba para la gráfica (Luego los traeremos de movimientos_inventario)
        categorias = ['Ene', 'Feb', 'Mar', 'Abr', 'May']
        entradas = [12, 19, 3, 15, 22]
        salidas = [8, 11, 5, 12, 14]

        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        
        width = 0.35
        ax.bar([i - width/2 for i in range(len(categorias))], entradas, width, label='Entradas', color='#4361EE', edgecolor='white')
        ax.bar([i + width/2 for i in range(len(categorias))], salidas, width, label='Salidas', color='#E63946', edgecolor='white')

        ax.set_title('Flujo de Inventario Mensual', fontsize=12, pad=20, fontweight='bold', color='#1E293B')
        ax.set_xticks(range(len(categorias)))
        ax.set_xticklabels(categorias)
        ax.legend(frameon=False)
        
        # Limpiar bordes de la gráfica
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_facecolor('#FFFFFF')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)