"""
reportes.py — Generación de PDFs para el sistema SmartKardex
Requiere: pip install reportlab
"""

import os
import datetime
from tkinter import filedialog, messagebox

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from config.db_conexion import ConexionDB
from models.modelos import SistemaConfiguracion


# ── Paleta PDF ───────────────────────────────────────────────────────────────
AZUL      = colors.HexColor("#4361EE")
AZUL_LITE = colors.HexColor("#EEF2FF")
ROJO      = colors.HexColor("#EF4444")
ROJO_LITE = colors.HexColor("#FEF2F2")
VERDE     = colors.HexColor("#10B981")
VERDE_LITE= colors.HexColor("#ECFDF5")
GRIS      = colors.HexColor("#64748B")
GRIS_LITE = colors.HexColor("#F8FAFC")
NEGRO     = colors.HexColor("#1E293B")
BLANCO    = colors.white


def _nombre_empresa():
    """Devuelve el nombre de la organización o texto por defecto."""
    try:
        d = SistemaConfiguracion.obtener()
        if d and d.get("nombre_organizacion"):
            return d["nombre_organizacion"]
    except Exception:
        pass
    return "SmartKardex"


def _nit_empresa():
    try:
        d = SistemaConfiguracion.obtener()
        if d and d.get("codigo_area"):
            return d["codigo_area"]
    except Exception:
        pass
    return ""


def _pedir_ruta(nombre_sugerido: str) -> str | None:
    """Abre el diálogo para guardar el PDF."""
    ruta = filedialog.asksaveasfilename(
        title="Guardar reporte como...",
        defaultextension=".pdf",
        initialfile=nombre_sugerido,
        filetypes=[("PDF", "*.pdf")]
    )
    return ruta if ruta else None


# ============================================================================
# REPORTE KARDEX
# ============================================================================

def generar_kardex(id_producto: int, nombre_producto: str):
    """
    Genera un PDF con el historial completo de movimientos de un producto.
    Calcula el stock acumulado fila por fila.
    """
    ruta = _pedir_ruta(f"Kardex_{nombre_producto.replace(' ', '_')}.pdf")
    if not ruta:
        return

    # ── Obtener datos ────────────────────────────────────────────────────
    db     = ConexionDB()
    cursor = db.obtener_cursor()
    if not cursor:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
        return

    # Stock inicial (antes del primer movimiento registrado) — lo tomamos como 0
    # y calculamos el saldo acumulado cronológicamente
    cursor.execute("""
        SELECT DATE_FORMAT(m.fecha, '%d/%m/%Y %H:%i') AS fecha_hora,
               m.tipo_movimiento, m.cantidad, m.motivo
        FROM movimientos_inventario m
        WHERE m.id_producto = %s
        ORDER BY m.fecha ASC
    """, (id_producto,))
    movimientos = cursor.fetchall()

    # Stock actual del producto
    cursor.execute("SELECT stock, stock_minimo FROM productos WHERE id_producto=%s",
                   (id_producto,))
    prod = cursor.fetchone()
    stock_actual  = int(prod["stock"])       if prod else 0
    stock_minimo  = int(prod["stock_minimo"]) if prod else 0

    # Calcular saldo acumulado hacia atrás desde el stock actual
    # (reconstruimos partiendo del stock actual en reversa)
    saldo = stock_actual
    saldos_reversa = []
    for mov in reversed(movimientos):
        saldos_reversa.append(saldo)
        if mov["tipo_movimiento"] == "ENTRADA":
            saldo -= int(mov["cantidad"])
        else:
            saldo += int(mov["cantidad"])
    saldos = list(reversed(saldos_reversa))

    # ── Construir PDF ────────────────────────────────────────────────────
    doc  = SimpleDocTemplate(ruta, pagesize=letter,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()
    story   = []

    # Encabezado
    empresa = _nombre_empresa()
    nit     = _nit_empresa()
    hoy     = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # SOLUCIÓN: Agregamos leading=20 y spaceAfter=8
    story.append(Paragraph(empresa, ParagraphStyle("emp",
        fontSize=16, leading=20, spaceAfter=8, fontName="Helvetica-Bold", textColor=NEGRO,
        alignment=TA_LEFT)))
    
    if nit:
        story.append(Paragraph(f"NIT: {nit}", ParagraphStyle("nit",
            fontSize=9, leading=12, textColor=GRIS, alignment=TA_LEFT)))

    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=AZUL))
    story.append(Spacer(1, 0.3*cm))

    # Título (También le ajustamos el leading para que no se pegue abajo)
    story.append(Paragraph("REPORTE KARDEX", ParagraphStyle("titulo",
        fontSize=20, leading=24, fontName="Helvetica-Bold", textColor=AZUL,
        alignment=TA_CENTER)))
    story.append(Spacer(1, 0.3*cm))
    
    # Info del producto
    info_data = [
        ["Producto:", nombre_producto,  "Generado:", hoy],
        ["Stock actual:", str(stock_actual), "Stock mínimo:", str(stock_minimo)],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 8*cm, 3*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",  (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",  (0,0), (-1,-1), 10),
        ("TEXTCOLOR", (0,0), (0,-1), NEGRO),
        ("TEXTCOLOR", (1,0), (1,-1), AZUL),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS))
    story.append(Spacer(1, 0.3*cm))

    # Tabla de movimientos
    encabezado = [["#", "Fecha / Hora", "Tipo", "Cantidad", "Motivo", "Saldo"]]
    filas      = []

    if movimientos:
        for i, (mov, saldo_fila) in enumerate(zip(movimientos, saldos), 1):
            tipo = mov["tipo_movimiento"]
            filas.append([
                str(i),
                mov["fecha_hora"],
                tipo,
                str(mov["cantidad"]),
                mov["motivo"] or "—",
                str(saldo_fila),
            ])
    else:
        filas.append(["", "Sin movimientos registrados", "", "", "", ""])

    tabla_data = encabezado + filas
    col_ws     = [1*cm, 4*cm, 3*cm, 2.5*cm, 6*cm, 2*cm]
    tabla      = Table(tabla_data, colWidths=col_ws, repeatRows=1)

    estilo_tabla = TableStyle([
        # Encabezado
        ("BACKGROUND",   (0,0), (-1,0),  AZUL),
        ("TEXTCOLOR",    (0,0), (-1,0),  BLANCO),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,0),  9),
        ("ALIGN",        (0,0), (-1,0),  "CENTER"),
        ("BOTTOMPADDING",(0,0), (-1,0),  8),
        ("TOPPADDING",   (0,0), (-1,0),  8),
        # Filas
        ("FONTSIZE",     (0,1), (-1,-1), 9),
        ("ALIGN",        (0,1), (-1,-1), "CENTER"),
        ("ALIGN",        (4,1), (4,-1),  "LEFT"),
        ("BOTTOMPADDING",(0,1), (-1,-1), 6),
        ("TOPPADDING",   (0,1), (-1,-1), 6),
        ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [BLANCO, GRIS_LITE]),
    ])

    # Color por tipo de movimiento
    for i, fila in enumerate(filas, 1):
        if fila[2] == "ENTRADA":
            estilo_tabla.add("TEXTCOLOR", (2,i), (2,i), VERDE)
            estilo_tabla.add("FONTNAME",  (2,i), (2,i), "Helvetica-Bold")
        elif fila[2] == "SALIDA":
            estilo_tabla.add("TEXTCOLOR", (2,i), (2,i), ROJO)
            estilo_tabla.add("FONTNAME",  (2,i), (2,i), "Helvetica-Bold")

    tabla.setStyle(estilo_tabla)
    story.append(tabla)

    # Totales
    story.append(Spacer(1, 0.5*cm))
    total_entradas = sum(int(m["cantidad"]) for m in movimientos if m["tipo_movimiento"] == "ENTRADA")
    total_salidas  = sum(int(m["cantidad"]) for m in movimientos if m["tipo_movimiento"] == "SALIDA")

    totales = Table([
        ["Total Entradas:", str(total_entradas),
         "Total Salidas:", str(total_salidas),
         "Stock Final:", str(stock_actual)]
    ], colWidths=[3.5*cm, 2.5*cm, 3*cm, 2.5*cm, 3*cm, 2.5*cm])
    totales.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 10),
        ("TEXTCOLOR",  (1,0), (1,0),   VERDE),
        ("TEXTCOLOR",  (3,0), (3,0),   ROJO),
        ("TEXTCOLOR",  (5,0), (5,0),   AZUL),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("BACKGROUND", (0,0), (-1,-1), AZUL_LITE),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(totales)

    # Pie de página
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS))
    story.append(Paragraph(f"Documento generado automáticamente por {empresa} · {hoy}",
                            ParagraphStyle("pie", fontSize=7, textColor=GRIS,
                                           alignment=TA_CENTER)))

    doc.build(story)
    messagebox.showinfo("✅ PDF generado",
                        f"Reporte Kardex guardado en:\n{ruta}")
    os.startfile(ruta)   # Abre el PDF automáticamente en Windows


# ============================================================================
# ORDEN DE COMPRA
# ============================================================================

def generar_orden_compra(productos_alerta: list):
    """
    Genera una Orden de Compra en PDF con los productos en alerta de stock.
    productos_alerta: lista de dicts con keys id_producto, nombre,
                      nombre_categoria, stock, stock_minimo
    """
    if not productos_alerta:
        messagebox.showinfo("Sin alertas", "No hay productos con stock bajo.")
        return

    hoy  = datetime.datetime.now().strftime("%d/%m/%Y")
    hora = datetime.datetime.now().strftime("%H%M%S")
    num  = datetime.datetime.now().strftime("%Y%m%d")

    ruta = _pedir_ruta(f"OrdenCompra_{num}.pdf")
    if not ruta:
        return

    empresa = _nombre_empresa()
    nit     = _nit_empresa()

    doc   = SimpleDocTemplate(ruta, pagesize=letter,
                              leftMargin=2*cm, rightMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Encabezado empresa
    # SOLUCIÓN: Agregamos leading=20 y spaceAfter=8
    story.append(Paragraph(empresa, ParagraphStyle("emp2",
        fontSize=16, leading=20, spaceAfter=8, fontName="Helvetica-Bold", textColor=NEGRO)))
    
    if nit:
        story.append(Paragraph(f"NIT: {nit}", ParagraphStyle("nit2",
            fontSize=9, leading=12, textColor=GRIS)))
            
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=AZUL))
    story.append(Spacer(1, 0.3*cm))

    # Título y número (Ajustamos el leading)
    story.append(Paragraph("ORDEN DE COMPRA", ParagraphStyle("tit2",
        fontSize=20, leading=24, fontName="Helvetica-Bold", textColor=AZUL,
        alignment=TA_CENTER)))

    # Meta info
    meta = Table([
        ["Fecha de emisión:", hoy,
         "Total ítems:", str(len(productos_alerta))],
        ["Estado:", "PENDIENTE DE APROBACIÓN", "Prioridad:", "ALTA ⚠️"],
    ], colWidths=[4*cm, 6*cm, 3.5*cm, 4*cm])
    meta.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",   (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (-1,-1), AZUL_LITE),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#BFDBFE")),
    ]))
    story.append(meta)
    story.append(Spacer(1, 0.5*cm))

    # Tabla de productos
    encabezado = [["#", "Producto", "Categoría", "Stock\nActual",
                   "Mínimo\nRequerido", "Cantidad\nSugerida", "Estado"]]
    filas = []
    for i, p in enumerate(productos_alerta, 1):
        stock  = int(p["stock"])
        minimo = int(p["stock_minimo"])
        # Cantidad sugerida: suficiente para llegar al doble del mínimo
        sugerida = max(minimo * 2 - stock, minimo)
        estado   = "❌ AGOTADO" if stock == 0 else "⚠️ BAJO STOCK"
        filas.append([
            str(i),
            p["nombre"],
            p["nombre_categoria"] or "—",
            str(stock),
            str(minimo),
            str(sugerida),
            estado,
        ])

    tabla_data = encabezado + filas
    col_ws = [0.8*cm, 5.5*cm, 3.5*cm, 2*cm, 2*cm, 2.2*cm, 2.8*cm]
    tabla  = Table(tabla_data, colWidths=col_ws, repeatRows=1)

    estilo = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  AZUL),
        ("TEXTCOLOR",     (0,0), (-1,0),  BLANCO),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  9),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("ALIGN",         (1,1), (2,-1),  "LEFT"),
        ("BOTTOMPADDING", (0,0), (-1,0),  8),
        ("TOPPADDING",    (0,0), (-1,0),  8),
        ("FONTSIZE",      (0,1), (-1,-1), 9),
        ("BOTTOMPADDING", (0,1), (-1,-1), 6),
        ("TOPPADDING",    (0,1), (-1,-1), 6),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [BLANCO, GRIS_LITE]),
    ])

    for i, fila in enumerate(filas, 1):
        if fila[3] == "0":   # Agotado
            estilo.add("BACKGROUND", (0,i), (-1,i), ROJO_LITE)
            estilo.add("TEXTCOLOR",  (6,i), (6,i),  ROJO)
        else:
            estilo.add("TEXTCOLOR",  (6,i), (6,i),  colors.HexColor("#B45309"))
        estilo.add("TEXTCOLOR", (5,i), (5,i), AZUL)
        estilo.add("FONTNAME",  (5,i), (5,i), "Helvetica-Bold")

    tabla.setStyle(estilo)
    story.append(tabla)

    # Nota
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph(
        "📝  <b>Nota:</b> La columna <b>Cantidad Sugerida</b> es un estimado "
        "calculado automáticamente para alcanzar el doble del stock mínimo. "
        "Verifique con su proveedor antes de confirmar el pedido.",
        ParagraphStyle("nota", fontSize=8, textColor=GRIS,
                       leftIndent=0.5*cm)
    ))

    # Firma
    story.append(Spacer(1, 2*cm))
    firma = Table([
        ["_________________________", "", "_________________________"],
        ["Elaborado por",            "", "Aprobado por"],
        [empresa,                    "", ""],
    ], colWidths=[6*cm, 5*cm, 6*cm])
    firma.setStyle(TableStyle([
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("FONTNAME",   (0,1), (-1,1),  "Helvetica-Bold"),
        ("TEXTCOLOR",  (0,0), (-1,-1), GRIS),
    ]))
    story.append(firma)

    # Pie
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS))
    story.append(Paragraph(
        f"Documento generado automáticamente por {empresa} · {hoy}",
        ParagraphStyle("pie2", fontSize=7, textColor=GRIS, alignment=TA_CENTER)
    ))

    doc.build(story)
    messagebox.showinfo("✅ PDF generado",
                        f"Orden de Compra guardada en:\n{ruta}")
    os.startfile(ruta)


# ============================================================================
# BACKUP DE BASE DE DATOS
# ============================================================================

def hacer_backup_bd():
    """
    Exporta todas las tablas de la BD a un archivo .sql usando Python puro.
    No requiere mysqldump instalado.
    """
    ruta = filedialog.asksaveasfilename(
        title="Guardar backup como...",
        defaultextension=".sql",
        initialfile=f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
        filetypes=[("SQL", "*.sql"), ("Todos", "*.*")]
    )
    if not ruta:
        return

    try:
        db     = ConexionDB()
        cursor = db.obtener_cursor()
        if not cursor:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return

        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f"-- Backup generado por SmartKardex\n")
            f.write(f"-- Fecha: {ahora}\n")
            f.write("-- -----------------------------------------------\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")

            # Obtener tablas
            cursor.execute("SHOW TABLES")
            tablas = [list(row.values())[0] for row in cursor.fetchall()]

            for tabla in tablas:
                f.write(f"-- ── Tabla: {tabla} ──\n")

                # CREATE TABLE
                cursor.execute(f"SHOW CREATE TABLE `{tabla}`")
                create = cursor.fetchone()
                create_sql = list(create.values())[1]
                f.write(f"DROP TABLE IF EXISTS `{tabla}`;\n")
                f.write(f"{create_sql};\n\n")

                # INSERT datos
                cursor.execute(f"SELECT * FROM `{tabla}`")
                filas = cursor.fetchall()
                if filas:
                    for fila in filas:
                        valores = []
                        for v in fila.values():
                            if v is None:
                                valores.append("NULL")
                            elif isinstance(v, (int, float)):
                                valores.append(str(v))
                            elif isinstance(v, datetime.datetime):
                                valores.append(f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'")
                            elif isinstance(v, datetime.date):
                                valores.append(f"'{v.strftime('%Y-%m-%d')}'")
                            else:
                                escaped = str(v).replace("\\", "\\\\").replace("'", "\\'")
                                valores.append(f"'{escaped}'")
                        f.write(f"INSERT INTO `{tabla}` VALUES ({', '.join(valores)});\n")
                f.write("\n")

            f.write("SET FOREIGN_KEY_CHECKS=1;\n")

        messagebox.showinfo("✅ Backup completado",
                            f"Base de datos exportada en:\n{ruta}")
        os.startfile(os.path.dirname(ruta))  # Abre la carpeta

    except Exception as e:
        messagebox.showerror("Error en backup", f"No se pudo crear el backup:\n{e}")